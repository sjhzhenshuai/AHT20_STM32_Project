#include "i2c.h"
#include "delay.h"
#include "stm32f10x_i2c.h"

/* ============================ 硬件 I2C1 ============================
 * PB6 = I2C1_SCL，PB7 = I2C1_SDA（复用开漏，无需重映射）。
 * 由 STM32 的 I2C 外设产生时序，100 kHz。
 * 默认不编译，把 i2c.h 里的 AHT20_USE_HW_I2C 改为 1 即可切换。
 */
#if (AHT20_USE_HW_I2C != 0)

#define I2Cx            I2C1

/* 等待标志位，超时返回 1 */
static uint8_t hw_wait_flag(uint32_t flag, FlagStatus status, uint32_t timeout_us)
{
    while (I2C_GetFlagStatus(I2Cx, flag) != status) {
        if (timeout_us == 0u) {
            return 1u;
        }
        timeout_us--;
        delay_us(1u);
    }
    return 0u;
}

/* 总线恢复：SCL 补 9 个脉冲，直到 SDA 被释放 */
static void hw_bus_recover(void)
{
    GPIO_InitTypeDef gpio;
    uint8_t i;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
    gpio.GPIO_Pin   = GPIO_Pin_6 | GPIO_Pin_7;
    gpio.GPIO_Mode  = GPIO_Mode_Out_OD;
    gpio.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &gpio);

    GPIO_SetBits(GPIOB, GPIO_Pin_6 | GPIO_Pin_7);
    for (i = 0u; i < 9u; i++) {
        GPIO_ResetBits(GPIOB, GPIO_Pin_6);
        delay_us(2u);
        GPIO_SetBits(GPIOB, GPIO_Pin_6);
        delay_us(2u);
    }
}

void I2C_BusInit(void)
{
    GPIO_InitTypeDef gpio;
    I2C_InitTypeDef  i2c;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_I2C1, ENABLE);

    /* 如果上次复位时总线被拉死，先恢复 */
    hw_bus_recover();

    gpio.GPIO_Pin   = GPIO_Pin_6 | GPIO_Pin_7;
    gpio.GPIO_Mode  = GPIO_Mode_AF_OD;
    gpio.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &gpio);

    I2C_DeInit(I2Cx);
    i2c.I2C_Mode                = I2C_Mode_I2C;
    i2c.I2C_DutyCycle           = I2C_DutyCycle_2;
    i2c.I2C_OwnAddress1         = 0x0Au;
    i2c.I2C_Ack                 = I2C_Ack_Enable;
    i2c.I2C_AcknowledgedAddress = I2C_AcknowledgedAddress_7bit;
    i2c.I2C_ClockSpeed          = 100000u;
    I2C_Init(I2Cx, &i2c);
    I2C_Cmd(I2Cx, ENABLE);
    I2C_AcknowledgeConfig(I2Cx, ENABLE);
}

static uint8_t hw_start(void)
{
    if (hw_wait_flag(I2C_FLAG_BUSY, RESET, 2000u) != 0u) {
        return 2u;
    }
    I2C_GenerateSTART(I2Cx, ENABLE);
    if (hw_wait_flag(I2C_FLAG_SB, SET, 2000u) != 0u) {
        return 2u;
    }
    return 0u;
}

static uint8_t hw_send_addr(uint8_t dev_addr, uint8_t read)
{
    uint32_t timeout = 5000u;

    I2C_Send7bitAddress(I2Cx, dev_addr,
                        (read != 0u) ? I2C_Direction_Receiver : I2C_Direction_Transmitter);

    while ((I2Cx->SR1 & (I2C_SR1_ADDR | I2C_SR1_AF)) == 0u) {
        if (--timeout == 0u) {
            return 2u;
        }
    }
    if ((I2Cx->SR1 & I2C_SR1_AF) != 0u) {
        I2C_ClearFlag(I2Cx, I2C_FLAG_AF);
        return 1u;      /* 从机 NACK */
    }
    (void)I2Cx->SR2;    /* 读 SR2 清除 ADDR */
    return 0u;
}

uint8_t I2C_Write(uint8_t dev_addr, const uint8_t *data, uint16_t len)
{
    uint16_t i;
    uint8_t  err;

    err = hw_start();
    if (err != 0u) {
        return err;
    }
    err = hw_send_addr(dev_addr, 0u);
    if (err != 0u) {
        I2C_GenerateSTOP(I2Cx, ENABLE);
        return err;
    }
    for (i = 0u; i < len; i++) {
        if (hw_wait_flag(I2C_FLAG_TXE, SET, 2000u) != 0u) {
            I2C_GenerateSTOP(I2Cx, ENABLE);
            return 2u;
        }
        I2C_SendData(I2Cx, data[i]);
        if (hw_wait_flag(I2C_FLAG_BTF, SET, 2000u) != 0u) {
            I2C_GenerateSTOP(I2Cx, ENABLE);
            return 2u;
        }
        if ((I2Cx->SR1 & I2C_SR1_AF) != 0u) {
            I2C_ClearFlag(I2Cx, I2C_FLAG_AF);
            I2C_GenerateSTOP(I2Cx, ENABLE);
            return 1u;
        }
    }
    I2C_GenerateSTOP(I2Cx, ENABLE);
    (void)hw_wait_flag(I2C_FLAG_BUSY, RESET, 2000u);
    return 0u;
}

uint8_t I2C_Read(uint8_t dev_addr, uint8_t *data, uint16_t len)
{
    uint16_t i;
    uint8_t  err;

    if (len == 0u) {
        return 0u;
    }

    err = hw_start();
    if (err != 0u) {
        return err;
    }
    err = hw_send_addr(dev_addr, 1u);
    if (err != 0u) {
        I2C_GenerateSTOP(I2Cx, ENABLE);
        return err;
    }

    for (i = 0u; i < len; i++) {
        if (i == (uint16_t)(len - 1u)) {
            I2C_AcknowledgeConfig(I2Cx, DISABLE);   /* 最后一个字节回 NACK */
        }
        if (hw_wait_flag(I2C_FLAG_RXNE, SET, 2000u) != 0u) {
            I2C_GenerateSTOP(I2Cx, ENABLE);
            I2C_AcknowledgeConfig(I2Cx, ENABLE);
            return 2u;
        }
        data[i] = I2C_ReceiveData(I2Cx);
    }

    I2C_GenerateSTOP(I2Cx, ENABLE);
    I2C_AcknowledgeConfig(I2Cx, ENABLE);
    (void)hw_wait_flag(I2C_FLAG_BUSY, RESET, 2000u);
    return 0u;
}

uint8_t I2C_Probe(uint8_t dev_addr)
{
    uint8_t err;

    err = hw_start();
    if (err != 0u) {
        return err;
    }
    err = hw_send_addr(dev_addr, 0u);
    I2C_GenerateSTOP(I2Cx, ENABLE);
    return err;
}

#endif /* AHT20_USE_HW_I2C != 0 */
