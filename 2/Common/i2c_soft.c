#include "i2c.h"
#include "delay.h"

/* ============================ 软件模拟 I2C ============================
 * PB6 = SCL，PB7 = SDA，均配置为开漏输出。
 * 每个电平变化后延时约 2 us，SCL 频率约 100 kHz。
 * 开漏输出 + 模块上拉电阻，从机才能把 SDA 拉低产生 ACK。
 */
#if (AHT20_USE_HW_I2C == 0)

#define I2C_GPIO        GPIOB
#define I2C_SCL_PIN     GPIO_Pin_6
#define I2C_SDA_PIN     GPIO_Pin_7

#define SCL_H()         (I2C_GPIO->BSRR = I2C_SCL_PIN)
#define SCL_L()         (I2C_GPIO->BRR  = I2C_SCL_PIN)
#define SDA_H()         (I2C_GPIO->BSRR = I2C_SDA_PIN)
#define SDA_L()         (I2C_GPIO->BRR  = I2C_SDA_PIN)
#define SDA_READ()      (((I2C_GPIO->IDR & I2C_SDA_PIN) != 0u) ? 1u : 0u)

#define I2C_DELAY()     delay_us(2u)

/* 总线恢复：若 SDA 被从机拉死，补 9 个时钟让其释放 */
static void soft_bus_recover(void)
{
    uint8_t i;

    SDA_H();
    for (i = 0u; i < 9u; i++) {
        SCL_L();
        delay_us(2u);
        SCL_H();
        delay_us(2u);
    }
}

void I2C_BusInit(void)
{
    GPIO_InitTypeDef gpio;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);

    gpio.GPIO_Pin   = I2C_SCL_PIN | I2C_SDA_PIN;
    gpio.GPIO_Mode  = GPIO_Mode_Out_OD;
    gpio.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(I2C_GPIO, &gpio);

    SDA_H();
    SCL_H();
    delay_us(10u);

    if (SDA_READ() == 0u) {
        soft_bus_recover();
    }
}

static void soft_start(void)
{
    SDA_H();
    SCL_H();
    I2C_DELAY();
    SDA_L();            /* SCL 为高时 SDA 下降沿 = 起始条件 */
    I2C_DELAY();
    SCL_L();
    I2C_DELAY();
}

static void soft_stop(void)
{
    SCL_L();
    SDA_L();
    I2C_DELAY();
    SCL_H();
    I2C_DELAY();
    SDA_H();            /* SCL 为高时 SDA 上升沿 = 停止条件 */
    I2C_DELAY();
}

/* 发送一个字节，返回 0 表示从机 ACK，1 表示 NACK */
static uint8_t soft_send_byte(uint8_t byte)
{
    uint8_t i;
    uint8_t ack;

    for (i = 0u; i < 8u; i++) {
        SCL_L();
        if ((byte & 0x80u) != 0u) {
            SDA_H();
        } else {
            SDA_L();
        }
        byte <<= 1;
        I2C_DELAY();
        SCL_H();
        I2C_DELAY();
    }

    /* 第 9 个时钟：释放 SDA，读从机应答 */
    SCL_L();
    SDA_H();
    I2C_DELAY();
    SCL_H();
    I2C_DELAY();
    ack = SDA_READ();
    SCL_L();
    I2C_DELAY();

    return ack;
}

/* 读一个字节；nack = 1 时主机在第 9 个时钟回 NACK */
static uint8_t soft_recv_byte(uint8_t nack)
{
    uint8_t i;
    uint8_t value = 0u;

    SDA_H();
    for (i = 0u; i < 8u; i++) {
        value <<= 1;
        I2C_DELAY();
        SCL_H();
        I2C_DELAY();
        if (SDA_READ() != 0u) {
            value |= 1u;
        }
        SCL_L();
        I2C_DELAY();
    }

    if (nack != 0u) {
        SDA_H();
    } else {
        SDA_L();
    }
    I2C_DELAY();
    SCL_H();
    I2C_DELAY();
    SCL_L();
    I2C_DELAY();
    SDA_H();

    return value;
}

uint8_t I2C_Write(uint8_t dev_addr, const uint8_t *data, uint16_t len)
{
    uint16_t i;

    soft_start();
    if (soft_send_byte((uint8_t)(dev_addr << 1)) != 0u) {
        soft_stop();
        return 1u;
    }
    for (i = 0u; i < len; i++) {
        if (soft_send_byte(data[i]) != 0u) {
            soft_stop();
            return 1u;
        }
    }
    soft_stop();
    return 0u;
}

uint8_t I2C_Read(uint8_t dev_addr, uint8_t *data, uint16_t len)
{
    uint16_t i;

    if (len == 0u) {
        return 0u;
    }

    soft_start();
    if (soft_send_byte((uint8_t)((dev_addr << 1) | 0x01u)) != 0u) {
        soft_stop();
        return 1u;
    }
    for (i = 0u; i < len; i++) {
        data[i] = soft_recv_byte((i == (uint16_t)(len - 1u)) ? 1u : 0u);
    }
    soft_stop();
    return 0u;
}

uint8_t I2C_Probe(uint8_t dev_addr)
{
    uint8_t ack;

    soft_start();
    ack = soft_send_byte((uint8_t)(dev_addr << 1));
    soft_stop();
    return ack;
}

#endif /* AHT20_USE_HW_I2C == 0 */
