/*
 * 任务一：STM32F103C8T6 + uC/OS-II 多任务实验
 *
 * 硬件连接：
 *   LED1 : PC13，板载 LED，低电平点亮
 *   LED2 : PA8 ，外接 LED（PA8 -- 220~1kΩ -- LED -- GND），高电平点亮
 *   USART1: PA9(TX) / PA10(RX)，115200-8-N-1
 *
 * 三个任务：
 *   TaskLED1  : 每 1 s 翻转一次 PC13
 *   TaskLED2  : 每 3 s 翻转一次 PA8
 *   TaskHello : 每 2 s 通过 USART1 发送 "hello uc/OS! 欢迎来到RTOS多任务环境！"
 *
 * 注意：串口中文按 UTF-8 发送；XCOM 需选择“编码方式 → UTF-8”，
 *       否则默认按 GBK 显示会出现中文乱码。
 */

#include "stm32f10x.h"
#include "ucos_ii.h"
#include "delay.h"
#include "usart.h"
#include "led.h"
#include <stdio.h>

/* 任务优先级：数值越小优先级越高 */
#define TASK_LED1_PRIO       5u
#define TASK_LED2_PRIO       6u
#define TASK_HELLO_PRIO      7u

/* 每个任务堆栈 512 个 OS_STK（32 位），即 2 KB */
#define TASK_STK_SIZE        512u

static OS_STK TaskLED1Stk[TASK_STK_SIZE];
static OS_STK TaskLED2Stk[TASK_STK_SIZE];
static OS_STK TaskHelloStk[TASK_STK_SIZE];

/* 调试计数：可用 DAPLink 直接读取，验证三个任务的实际运行周期 */
volatile uint32_t g_task_led1_count = 0u;
volatile uint32_t g_task_led2_count = 0u;
volatile uint32_t g_task_hello_count = 0u;

/*
 * SysTick 中断服务程序。
 * uC/OS-II 的系统节拍由 SysTick 产生，OS_CPU_SysTickHandler() 内部会
 * 调用 OSIntEnter()、OSTimeTick() 和 OSIntExit()。
 */
void SysTick_Handler(void)
{
    OS_CPU_SysTickHandler();
}

/* 任务 1：1 s 周期翻转 LED1（PC13） */
static void TaskLED1(void *p_arg)
{
    (void)p_arg;

    while (1) {
        g_task_led1_count++;
        LED1_Toggle();                         /* 亮 -> 灭，或 灭 -> 亮 */
        OSTimeDlyHMSM(0u, 0u, 1u, 0u);         /* 延时 1 s，让出 CPU */
    }
}

/* 任务 2：3 s 周期翻转 LED2（PA8） */
static void TaskLED2(void *p_arg)
{
    (void)p_arg;

    while (1) {
        g_task_led2_count++;
        LED2_Toggle();
        OSTimeDlyHMSM(0u, 0u, 3u, 0u);         /* 延时 3 s */
    }
}

/* 任务 3：2 s 周期通过 USART1 发送指定字符串 */
static void TaskHello(void *p_arg)
{
    (void)p_arg;

    while (1) {
        g_task_hello_count++;
        printf("hello uc/OS! 欢迎来到RTOS多任务环境！\r\n");
        OSTimeDlyHMSM(0u, 0u, 2u, 0u);         /* 延时 2 s */
    }
}

int main(void)
{
    INT8U err;

    /* 1. 底层初始化：延时、串口、LED */
    delay_init();                              /* DWT 延时，避免占用 SysTick */
    USART1_Init(115200u);
    LED_Init();

    printf("\r\n==============================================\r\n");
    printf(" STM32F103C8T6 + uC/OS-II 多任务实验（任务一）\r\n");
    printf(" SystemCoreClock = %lu Hz, OS_TICKS_PER_SEC = %u\r\n",
           (unsigned long)SystemCoreClock, (unsigned)OS_TICKS_PER_SEC);
    printf(" LED1: PC13 / 1 s   LED2: PA8 / 3 s   UART: 2 s\r\n");
    printf("==============================================\r\n");

    /* 2. 初始化 uC/OS-II 内核 */
    OSInit();

    /* 3. 创建 3 个任务（堆栈从高地址向下增长，故传 &Stk[SIZE-1]） */
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

    err = OSTaskCreate(TaskHello, (void *)0,
                       &TaskHelloStk[TASK_STK_SIZE - 1u], TASK_HELLO_PRIO);
    if (err != OS_ERR_NONE) {
        printf("TaskHello create error = %u\r\n", err);
    }

    /* 4. 配置并启动 SysTick（1 ms 节拍），然后启动调度器 */
    OS_CPU_SysTickInitFreq(SystemCoreClock);
    OSStart();

    /* OSStart() 正常不会返回 */
    while (1) {
    }
}