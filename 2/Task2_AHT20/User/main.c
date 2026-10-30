/*
 * 任务二：STM32F103C8T6 + uC/OS-II + AHT20 温湿度采集
 *
 * 硬件连接：
 *   LED1  : PC13，板载 LED，低电平点亮
 *   LED2  : PA8 ，外接 LED，高电平点亮
 *   USART1: PA9(TX) / PA10(RX)，115200-8-N-1
 *   AHT20 : VCC=3.3V，GND=GND，SCL=PB6，SDA=PB7（软件 I2C）
 *
 * 三个任务（在任务一基础上，把第 3 个任务改为采集 AHT20）：
 *   TaskLED1  : 每 1 s 翻转 PC13
 *   TaskLED2  : 每 3 s 翻转 PA8
 *   TaskAHT20 : 每 2 s 采集一次温湿度并通过 USART1 发送
 */

#include "stm32f10x.h"
#include "ucos_ii.h"
#include "delay.h"
#include "usart.h"
#include "led.h"
#include "i2c.h"
#include "aht20.h"
#include <stdio.h>

#define TASK_LED1_PRIO       5u
#define TASK_LED2_PRIO       6u
#define TASK_AHT20_PRIO      7u

#define TASK_STK_SIZE        512u

static OS_STK TaskLED1Stk[TASK_STK_SIZE];
static OS_STK TaskLED2Stk[TASK_STK_SIZE];
static OS_STK TaskAHT20Stk[TASK_STK_SIZE];

volatile uint32_t g_task_led1_count  = 0u;
volatile uint32_t g_task_led2_count  = 0u;
volatile uint32_t g_task_aht20_count = 0u;

static volatile uint8_t g_aht20_ready = 0u;

void SysTick_Handler(void)
{
    OS_CPU_SysTickHandler();
}

static void AHT20_Print(const AHT20_Data *d)
{
    int32_t  t  = (int32_t)(d->temperature * 100.0f +
                            ((d->temperature >= 0.0f) ? 0.5f : -0.5f));
    int32_t  h  = (int32_t)(d->humidity * 100.0f + 0.5f);
    uint32_t ta = (t < 0) ? (uint32_t)(-t) : (uint32_t)t;

    printf("[%lu] AHT20: T=%s%lu.%02lu C, RH=%lu.%02lu %%  (CRC %s)\r\n",
           (unsigned long)g_task_aht20_count,
           (t < 0) ? "-" : "",
           (unsigned long)(ta / 100u), (unsigned long)(ta % 100u),
           (unsigned long)((uint32_t)h / 100u), (unsigned long)((uint32_t)h % 100u),
           (d->crc_ok != 0u) ? "OK" : "ERR");
}

static void TaskLED1(void *p_arg)
{
    (void)p_arg;
    while (1) {
        g_task_led1_count++;
        LED1_Toggle();
        OSTimeDlyHMSM(0u, 0u, 1u, 0u);
    }
}

static void TaskLED2(void *p_arg)
{
    (void)p_arg;
    while (1) {
        g_task_led2_count++;
        LED2_Toggle();
        OSTimeDlyHMSM(0u, 0u, 3u, 0u);
    }
}

/* 任务 3：每 2 s 采集一次 AHT20 并通过串口输出 */
static void TaskAHT20(void *p_arg)
{
    AHT20_Data data;
    uint8_t err;

    (void)p_arg;

    while (1) {
        if (g_aht20_ready == 0u) {
            err = AHT20_Init();
            if (err == AHT20_OK) {
                g_aht20_ready = 1u;
                printf("[AHT20] init OK (addr 0x38)\r\n");
            } else {
                printf("[AHT20] init failed: %s\r\n", AHT20_ErrString(err));
            }
        }

        if (g_aht20_ready != 0u) {
            err = AHT20_Read(&data);
            if (err == AHT20_OK) {
                g_task_aht20_count++;
                AHT20_Print(&data);
            } else {
                printf("[AHT20] read failed: %s\r\n", AHT20_ErrString(err));
                g_aht20_ready = 0u;     /* 下一轮重新初始化 */
            }
        }

        OSTimeDlyHMSM(0u, 0u, 2u, 0u);
    }
}

int main(void)
{
    INT8U err;

    delay_init();
    USART1_Init(115200u);
    LED_Init();

    printf("\r\n==============================================\r\n");
    printf(" STM32F103C8T6 + uC/OS-II + AHT20（任务二）\r\n");
    printf(" SystemCoreClock = %lu Hz, OS_TICKS_PER_SEC = %u\r\n",
           (unsigned long)SystemCoreClock, (unsigned)OS_TICKS_PER_SEC);
    printf(" LED1: PC13/1s  LED2: PA8/3s  AHT20: 2s\r\n");
    printf(" I2C: software bit-bang, SCL=PB6, SDA=PB7\r\n");
    printf("==============================================\r\n");

    /* 先检查总线上有哪些器件，接线有问题时可直接看出来 */
    I2C_BusInit();
    delay_ms(100);
    I2C_BusScan();

    OSInit();

    err = OSTaskCreate(TaskLED1, (void *)0,
                       &TaskLED1Stk[TASK_STK_SIZE - 1u], TASK_LED1_PRIO);
    if (err != OS_ERR_NONE) {
        printf("TaskLED1 create error = %u\r\n", err);
    }

    err = OSTaskCreate(TaskLED2, (void *)0,
                       &TaskLED2Stk[TASK_STK_SIZE - 1u], TASK_LED2_PRIO);
    if (err != OS_ERR_NONE) {
        printf("TaskLED2 create error = %u\r\n", err);
    }

    err = OSTaskCreate(TaskAHT20, (void *)0,
                       &TaskAHT20Stk[TASK_STK_SIZE - 1u], TASK_AHT20_PRIO);
    if (err != OS_ERR_NONE) {
        printf("TaskAHT20 create error = %u\r\n", err);
    }

    OS_CPU_SysTickInitFreq(SystemCoreClock);
    OSStart();

    while (1) {
    }
}
