#include "delay.h"

/* SysTick 已归 uC/OS-II 使用。DWT 周期计数器为软件 I2C 提供短延时，
 * 不占用 RTOS 的节拍中断。 */
void delay_init(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0u;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void delay_us(uint32_t nus)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = (SystemCoreClock / 1000000u) * nus;
    while ((uint32_t)(DWT->CYCCNT - start) < cycles) {
        __NOP();
    }
}

void delay_ms(uint16_t nms)
{
    while (nms-- != 0u) {
        delay_us(1000u);
    }
}