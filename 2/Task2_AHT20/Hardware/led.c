#include "led.h"

/* LED1：STM32F103C8T6 Blue-Pill PC13，低电平点亮。
 * LED2：PA8 外接 LED（串联电阻到 GND），高电平点亮。 */
void LED_Init(void)
{
    GPIO_InitTypeDef gpio;
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC, ENABLE);

    gpio.GPIO_Pin = GPIO_Pin_13;
    gpio.GPIO_Mode = GPIO_Mode_Out_PP;
    gpio.GPIO_Speed = GPIO_Speed_2MHz;
    GPIO_Init(GPIOC, &gpio);

    gpio.GPIO_Pin = GPIO_Pin_8;
    GPIO_Init(GPIOA, &gpio);

    GPIO_SetBits(GPIOC, GPIO_Pin_13);
    GPIO_ResetBits(GPIOA, GPIO_Pin_8);
}

void LED1_Toggle(void)
{
    GPIOC->ODR ^= GPIO_Pin_13;
}

void LED2_Toggle(void)
{
    GPIOA->ODR ^= GPIO_Pin_8;
}