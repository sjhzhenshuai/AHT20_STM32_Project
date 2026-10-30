# 任务一：uC/OS-II 在 STM32F103C8T6 上的移植与多任务实验

## 1. 实验目的

1. 学习嵌入式实时操作系统（RTOS）的基本概念：任务、优先级、调度、系统节拍、上下文切换和临界区。
2. 以 uC/OS-II 为例，掌握 RTOS 在 ARM Cortex-M3（STM32F103）上的移植方法。
3. 构建 3 个应用任务，分别以 1 s、3 s、2 s 为周期控制 LED 和串口输出，验证多任务并发运行。
4. 学会使用 Keil MDK、DAPLink（CMSIS-DAP）完成编译、下载、在线调试和运行验证。

## 2. 实验环境

| 项目 | 配置 |
|---|---|
| MCU | STM32F103C8T6，64 KB Flash，20 KB SRAM，Cortex-M3 |
| 系统时钟 | HSE 8 MHz，PLL ×9，SYSCLK = 72 MHz |
| 开发环境 | Keil MDK 5.38，ARM Compiler 6.19（AC6） |
| RTOS | uC/OS-II V2.93.01（Apache-2.0），ARM Cortex-M/ARMv7-M 端口 |
| 下载器 | DAPLink（CMSIS-DAP，SWD 接口） |
| 串口 | USART1，PA9(TX)/PA10(RX)，115200-8-N-1，UTF-8 |
| 工程路径 | `F:\Keil files\AHT20\Task1_uCOSII` |

## 3. 硬件连接

| 信号 | STM32F103C8T6 引脚 | 说明 |
|---|---|---|
| LED1 | PC13 | 板载 LED，低电平点亮 |
| LED2 | PA8 | 外接 LED：PA8 → 220 Ω～1 kΩ → LED → GND，高电平点亮 |
| USART1_TX | PA9 | 接 USB-TTL 的 RX |
| USART1_RX | PA10 | 接 USB-TTL 的 TX（本实验只发送，可不接） |
| GND | GND | STM32、USB-TTL、DAPLink 必须共地 |
| SWDIO | PA13 | DAPLink SWDIO |
| SWCLK | PA14 | DAPLink SWCLK |
| BOOT0 | BOOT0 跳线 | **必须接 0/GND**，否则复位后进入系统 Bootloader，不运行 Flash 程序 |

> 说明：DAPLink 的 USB 转串口（本机为 COM4）并不等于已经接到 PA9/PA10。若 DAPLink 板上没有把 UART 引到目标板，需要另接 USB-TTL，或者把 DAPLink 的 UART TX/RX 分别接到 PA10/PA9。

## 4. uC/OS-II 移植原理

### 4.1 uC/OS-II 的层次

uC/OS-II 的源码分为与 CPU 无关的内核和与 CPU 相关的端口两层：

- 与 CPU 无关：`os_core.c`、`os_task.c`、`os_time.c`、`os_sem.c`、`os_mutex.c`、`os_q.c`、`os_flag.c`、`os_mem.c`、`os_tmr.c` 等。
- 与 CPU 相关：
  - `os_cpu.h`：数据类型、堆栈增长方向、临界区宏、函数声明。
  - `os_cpu_c.c`：`OS_CPU_SysTickHandler()`、`OS_CPU_SysTickInit()`、`OSTaskStkInit()` 等。
  - `os_cpu_a.asm`：`OSStartHighRdy()`、`OSCtxSw()`、`OSIntCtxSw()`、`OS_CPU_PendSVHandler()`、`OS_CPU_SR_Save/Restore()`。
  - `cpu_c.c` / `cpu_a.asm` / `cpu_core.c`：CPU 底层初始化、时间戳、异常栈等。
- 与编译器/库相关：`lib_mem.c`、`lib_str.c`、`lib_ascii.c`。

本工程使用的端口目录为：

```text
Middlewares/uC-OS2/
├─ uC-CPU/
│  ├─ cpu_core.c
│  ├─ cpu_core.h
│  ├─ cpu_def.h
│  └─ ARM-Cortex-M/ARMv7-M/
│     ├─ cpu_c.c
│     └─ ARM/cpu_a.asm、cpu.h
├─ uC-LIB/
│  ├─ lib_mem.c、lib_str.c、lib_ascii.c
│  └─ ...
└─ uC-OS2/
   ├─ Source/ucos_ii.c、os_dbg_r.c ...
   └─ Ports/ARM-Cortex-M/ARMv7-M/
      ├─ os_cpu_c.c
      └─ ARM/os_cpu_a.asm、os_cpu.h
```

### 4.2 Cortex-M3 上的任务切换

Cortex-M3 有两个堆栈指针：

- MSP：主堆栈，异常/中断使用。
- PSP：进程堆栈，任务使用。

uC/OS-II 的任务切换利用 PendSV 异常完成：

1. 任务调用 `OSTimeDly()` 等函数后，内核调用 `OSCtxSw()`。
2. `OSCtxSw()` 向 `NVIC_INT_CTRL` 的 `PENDSVSET` 位写 1，挂起 PendSV 异常。
3. PendSV 优先级被设为最低，因此会等所有其他中断处理完再执行。
4. `OS_CPU_PendSVHandler()` 把当前任务的 R4～R11、R14 压入该任务的 PSP 堆栈，把 PSP 保存到当前 TCB。
5. 从高优先级就绪任务的 TCB 取出 PSP，恢复 R4～R11、R14，更新 `OSTCBCur`、`OSPrioCur`。
6. 异常返回时，Cortex-M3 自动从 PSP 恢复 R0～R3、R12、LR、PC、xPSR，开始运行新任务。

Cortex-M3 在进入异常时会自动保存一半寄存器（R0～R3、R12、LR、PC、xPSR），所以 PendSV 只需要手动保存 R4～R11 和 R14，这也是 Cortex-M 端口效率高的原因。

### 4.3 系统节拍

uC/OS-II 需要周期性节拍来维护延时和超时。本工程使用 SysTick：

- `OS_TICKS_PER_SEC = 1000`，即 1 ms 一个节拍。
- `OS_CPU_SysTickInitFreq(SystemCoreClock)` 计算 `72000000 / 1000 = 72000`，写入 `SysTick->LOAD = 72000 - 1 = 71999`。
- `SysTick_Handler()` 调用 `OS_CPU_SysTickHandler()`，后者依次调用 `OSIntEnter()`、`OSTimeTick()`、`OSIntExit()`。
- 实测 `SYST_CSR = 0x00010007`（COUNTFLAG、CLKSOURCE、TICKINT、ENABLE），`SYST_RVR = 71999`，说明 1 ms 节拍正确。

### 4.4 临界区

本工程使用临界区方法 3（BASEPRI）：

- `CPU_CFG_KA_IPL_BOUNDARY = 1`，`CPU_CFG_NVIC_PRIO_BITS = 4`。
- `OS_ENTER_CRITICAL()` 调用 `OS_CPU_SR_Save(0x10)`，把 BASEPRI 设为 `0x10`，屏蔽优先级数值不小于 0x10 的中断，同时保存旧 BASEPRI。
- `OS_EXIT_CRITICAL()` 调用 `OS_CPU_SR_Restore()` 恢复旧 BASEPRI。
- 这样既保护了内核临界区，又不会把所有中断都关掉，保留了高优先级中断的实时性。

### 4.5 堆栈增长方向

`os_cpu.h` 中 `OS_STK_GROWTH = 1`，表示堆栈从高地址向低地址增长（满递减堆栈）。因此创建任务时传入的是堆栈数组的**最后一个元素**地址：

```c
OSTaskCreate(TaskLED1, (void *)0, &TaskLED1Stk[TASK_STK_SIZE - 1u], 5u);
```

## 5. 移植过程

### 5.1 建立 Keil 工程

1. 打开 Keil MDK，新建 STM32F103C8 工程。
2. 选择 CMSIS 启动文件 `startup_stm32f10x_md.s`（中容量）。
3. 添加 `system_stm32f10x.c`、`core_cm3.c`。
4. 添加 STM32F10x 标准外设库的 `stm32f10x_rcc.c`、`stm32f10x_gpio.c`、`stm32f10x_usart.c`、`misc.c`。
5. 在 `system_stm32f10x.c` 中保持 `SYSCLK_FREQ_72MHz`，系统时钟设为 72 MHz。
6. 在 `stm32f10x_conf.h` 中打开 RCC、GPIO、USART、MISC 等头文件。

工程的目标器件为 `STM32F103C8`，IROM 为 `0x08000000`、大小 `0x10000`（64 KB），IRAM 为 `0x20000000`、大小 `0x5000`（20 KB）。

### 5.2 加入 uC/OS-II 源码

把 uC/OS-II、uC/CPU、uC/LIB 复制到工程的 `Middlewares/uC-OS2` 下，并在 Keil 工程中建立 `uC-OS-II` 分组，加入以下文件：

| 文件 | 作用 |
|---|---|
| `uC-CPU/cpu_core.c` | CPU 内核支持、异常栈等 |
| `uC-CPU/ARM-Cortex-M/ARMv7-M/cpu_c.c` | CPU 端口 C 代码 |
| `uC-CPU/ARM-Cortex-M/ARMv7-M/ARM/cpu_a.asm` | CPU 端口汇编 |
| `uC-OS2/Source/ucos_ii.c` | 内核总入口（包含各内核 C 文件） |
| `uC-OS2/Source/os_dbg_r.c` | 调试变量 |
| `uC-OS2/Ports/ARM-Cortex-M/ARMv7-M/os_cpu_c.c` | uC/OS-II 端口 C 代码 |
| `uC-OS2/Ports/ARM-Cortex-M/ARMv7-M/ARM/os_cpu_a.asm` | uC/OS-II 端口汇编 |
| `uC-LIB/lib_mem.c`、`lib_str.c`、`lib_ascii.c` | 内存/字符串/字符库 |

> `ucos_ii.c` 已经通过 `#include` 把 `os_core.c`、`os_task.c`、`os_time.c` 等内核源文件包含进来，所以工程中只需要加入 `ucos_ii.c`，不要重复加入各个 `os_*.c`。

### 5.3 添加配置文件

在 `User` 目录下准备以下配置文件：

#### `os_cfg.h`

关键配置：

```c
#define OS_TICKS_PER_SEC        1000u   /* 1 ms 一个节拍 */
#define OS_LOWEST_PRIO          63u     /* 优先级 0～63 */
#define OS_TASK_STAT_EN         1u      /* 使能统计任务 */
#define OS_TASK_NAME_EN         1u
#define OS_DEBUG_EN             1u
#define OS_TMR_EN               1u
#define OS_EVENT_NAME_EN        1u
```

#### `app_cfg.h`

```c
#include <stdarg.h>
#include <stdio.h>
#include <cpu.h>

#define APP_CFG_STARTUP_TASK_PRIO       3u
#define OS_TASK_TMR_PRIO               (OS_LOWEST_PRIO - 2u)
#define APP_CFG_STARTUP_TASK_STK_SIZE   128u
```

#### `cpu_cfg.h`

```c
#define CPU_CFG_KA_IPL_BOUNDARY         1u
#define CPU_CFG_NVIC_PRIO_BITS          4u
#define CPU_CFG_TS_32_EN                DEF_DISABLED
#define CPU_CFG_TS_64_EN                DEF_DISABLED
#define CPU_CFG_CACHE_MGMT_EN           DEF_DISABLED
```

#### `stm32f10x_conf.h`

打开 RCC、GPIO、USART、MISC 等模块，并把 `assert_param` 定义为空，减小代码体积：

```c
#define assert_param(expr) ((void)0)
```

### 5.4 修改启动文件的向量表

STM32 启动文件 `startup_stm32f10x_md.s` 中，PendSV 向量默认指向弱定义的 `PendSV_Handler`。uC/OS-II 要求 PendSV 指向 `OS_CPU_PendSVHandler`：

```asm
IMPORT  OS_CPU_PendSVHandler

DCD     SVC_Handler                ; SVCall Handler
DCD     DebugMon_Handler           ; Debug Monitor Handler
DCD     0                          ; Reserved
DCD     OS_CPU_PendSVHandler      ; uC/OS-II PendSV Handler
DCD     SysTick_Handler            ; SysTick Handler
```

SysTick 仍然使用启动文件中的弱定义 `SysTick_Handler`，在 `main.c` 中重新定义并调用 `OS_CPU_SysTickHandler()`：

```c
void SysTick_Handler(void)
{
    OS_CPU_SysTickHandler();
}
```

> 注意：如果忘记把 PendSV 向量改成 `OS_CPU_PendSVHandler`，系统可能能启动，但任务切换时会进入默认的 `PendSV_Handler` 死循环，表现为只有第一个任务运行或直接死机。

### 5.5 配置 SysTick

在 `main()` 中，创建完任务后、调用 `OSStart()` 之前：

```c
OS_CPU_SysTickInitFreq(SystemCoreClock);
OSStart();
```

`OS_CPU_SysTickInitFreq()` 会：

1. 计算 `cnts = cpu_freq / OS_TICKS_PER_SEC`。
2. 写 `SysTick->LOAD = cnts - 1`。
3. 设置 SysTick 中断优先级。
4. 选择处理器时钟作为 SysTick 时钟源。
5. 使能 SysTick 计数和中断。

### 5.6 编写三个任务

任务优先级和堆栈：

| 任务 | 优先级 | 堆栈 | 周期 | 功能 |
|---|---|---|---|---|
| `TaskLED1` | 5 | 512 OS_STK（2 KB） | 1 s | 翻转 PC13 板载 LED |
| `TaskLED2` | 6 | 512 OS_STK（2 KB） | 3 s | 翻转 PA8 外接 LED |
| `TaskHello` | 7 | 512 OS_STK（2 KB） | 2 s | USART1 发送指定字符串 |

核心代码：

```c
#define TASK_LED1_PRIO       5u
#define TASK_LED2_PRIO       6u
#define TASK_HELLO_PRIO      7u
#define TASK_STK_SIZE        512u

static OS_STK TaskLED1Stk[TASK_STK_SIZE];
static OS_STK TaskLED2Stk[TASK_STK_SIZE];
static OS_STK TaskHelloStk[TASK_STK_SIZE];

static void TaskLED1(void *p_arg)
{
    (void)p_arg;
    while (1) {
        LED1_Toggle();
        OSTimeDlyHMSM(0u, 0u, 1u, 0u);
    }
}

static void TaskLED2(void *p_arg)
{
    (void)p_arg;
    while (1) {
        LED2_Toggle();
        OSTimeDlyHMSM(0u, 0u, 3u, 0u);
    }
}

static void TaskHello(void *p_arg)
{
    (void)p_arg;
    while (1) {
        printf("hello uc/OS! 欢迎来到RTOS多任务环境！\r\n");
        OSTimeDlyHMSM(0u, 0u, 2u, 0u);
    }
}
```

`main()` 中创建任务：

```c
OSInit();

OSTaskCreate(TaskLED1,  (void *)0, &TaskLED1Stk[TASK_STK_SIZE - 1u],  TASK_LED1_PRIO);
OSTaskCreate(TaskLED2,  (void *)0, &TaskLED2Stk[TASK_STK_SIZE - 1u],  TASK_LED2_PRIO);
OSTaskCreate(TaskHello, (void *)0, &TaskHelloStk[TASK_STK_SIZE - 1u], TASK_HELLO_PRIO);

OS_CPU_SysTickInitFreq(SystemCoreClock);
OSStart();
```

任务调度分析：

- 三个任务都调用 `OSTimeDlyHMSM()` 主动阻塞，CPU 在三个任务和空闲任务之间切换。
- 优先级 5、6、7 均高于统计任务和空闲任务；当三个任务都延时阻塞时，内核运行空闲任务。
- 1 ms 节拍下，1 s = 1000 个节拍，3 s = 3000 个节拍，2 s = 2000 个节拍。
- 任务切换和节拍中断的抖动小于 1 个节拍（约 1 ms），满足实验要求。

### 5.7 printf 串口重定向

在 `Hardware/usart.c` 中实现 `fputc()`：

```c
int fputc(int ch, FILE *f)
{
    while (USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET);
    USART_SendData(USART1, (uint8_t)ch);
    return ch;
}
```

然后在 Keil 中打开：

```text
Options for Target → Target → 勾选 Use MicroLIB
```

**为什么必须用 MicroLIB？**

如果使用标准 C 库，`printf` 初始化 `stdout` 时会调用 `_sys_open()`，而标准库的 `_sys_open()` 是半主机（semihosting）实现，内部是 `BKPT #0xAB`。没有调试器处理半主机时，程序会停在 `0x08000950` 的 `BKPT` 指令处，表现为：

- 程序不运行；
- `RCC_APB2ENR = 0`，USART、GPIO 时钟都没有使能；
- PC 停在 `0x08000950` 附近。

本工程最初就遇到了这个问题。勾选 MicroLIB 后，`printf` 直接使用 `fputc()`，不再走半主机，问题解决。

如果不想使用 MicroLIB，也可以重定向 `_sys_open`、`_sys_write` 等函数，或者使用 `__use_no_semihosting` 并补齐相关桩函数。

### 5.8 修正 Flash 起始地址（重要）

移植时发现，工程虽然把 Device 设成了 STM32F103C8，但 Keil 生成的 `.sct` 仍然是：

```text
LR_IROM1 0x00000000 0x00040000
```

而不是：

```text
LR_IROM1 0x08000000 0x00010000
```

这样生成的 `.hex` 从 `0x00000000` 开始，烧录时会报：

```text
No Algorithm found for: 00000000H - 00002E2FH
Erase skipped!
Error: Flash Download failed - "Cortex-M3"
```

原因是工程的 `OCR_RVCT4` / `OCR_RVCT9`（Read/Write Memory Layout）仍然是旧工程的 `0x00000000/0x00040000` 和 `0x20000000/0x00020000`。修正方法：

1. `Options for Target → Target` 中确认：
   - IROM1：Start `0x08000000`，Size `0x10000`；
   - IRAM1：Start `0x20000000`，Size `0x5000`。
2. `Options for Target → Linker` 中确认使用 Target 对话框的存储布局，或直接检查/修改工程文件中的 `OCR_RVCT4`、`OCR_RVCT9`。
3. 重新编译后打开 `Objects/Task1_uCOSII.sct`，确认第一行是 `LR_IROM1 0x08000000 0x00010000`。
4. 再打开 `Objects/Task1_uCOSII.hex`，确认第一行是 `:020000040800F2`（扩展线性地址 0x0800）。

修正后烧录日志为：

```text
Erase Done.
Programming Done.
Verify OK.
Flash Load finished
```

### 5.9 编译与下载

编译结果：

```text
Program Size: Code=8856 RO-data=764 RW-data=8 ZI-data=13376
".\Objects\Task1_uCOSII.axf" - 0 Error(s), 2 Warning(s).
```

两个警告都是 AC6 提示 `-D __UVISION_VERSION=538` 未使用，属于 Keil 自动添加的宏，无影响。

DAPLink 配置：

- `Options for Target → Debug`：选择 `CMSIS-DAP Debugger`，接口 `SWD`。
- `Options for Target → Utilities`：选择 `Use Target Driver for Flash Programming`，Flash 算法 `STM32F10x 128kB Flash`（该算法兼容 C8T6 的 64 KB Flash，实际只写 64 KB 范围）。
- 也可以用命令行烧录：

```text
UV4.exe -f Task1_uCOSII.uvprojx -j0 -o Objects\flash.log
```

## 6. 运行验证

### 6.1 向量表与 Flash 内容

用 DAPLink（pyOCD）读取 `0x08000000`：

```text
0x08000000: 0x20003450   ; 初始 MSP
0x08000004: 0x08000101   ; Reset_Handler（Thumb）
```

说明程序确实烧录在 `0x08000000`，向量表正确。

### 6.2 SysTick 与 GPIO 实测

运行时读取：

```text
SYST_CSR = 0x00010007   ; COUNTFLAG=1, CLKSOURCE=1, TICKINT=1, ENABLE=1
SYST_RVR = 71999        ; 72 MHz / 1000 - 1 = 1 ms
```

三个任务的调试计数变量（可通过 DAPLink 直接读取）：

| 变量 | 地址 | 含义 |
|---|---|---|
| `g_task_led1_count` | `0x20003040` | TaskLED1 翻转次数 |
| `g_task_led2_count` | `0x20003044` | TaskLED2 翻转次数 |
| `g_task_hello_count` | `0x2000303C` | TaskHello 发送次数 |
| `g_uart_tx_count` | `0x20003048` | fputc 实际发送的字节数 |

10 秒实测（每 0.5 s 采样一次，节选）：

| 时间 | LED1 计数 | LED2 计数 | HELLO 计数 | PA8 | PC13 |
|---|---|---|---|---|---|
| 0.5 s | 1 | 1 | 1 | ON | ON |
| 1.5 s | 2 | 1 | 1 | ON | OFF |
| 2.5 s | 3 | 1 | 2 | ON | ON |
| 3.5 s | 4 | 2 | 2 | OFF | OFF |
| 4.5 s | 5 | 2 | 3 | OFF | ON |
| 5.5 s | 6 | 2 | 3 | OFF | OFF |
| 6.5 s | 7 | 3 | 4 | ON | ON |
| 7.5 s | 8 | 3 | 4 | ON | OFF |
| 8.5 s | 9 | 3 | 5 | ON | ON |
| 9.5 s | 10 | 4 | 5 | OFF | OFF |
| 10.0 s | 11 | 4 | 5 | OFF | ON |

结论：

- `g_task_led1_count` 每秒增加 1，LED1 周期 1 s；
- `g_task_led2_count` 每 3 秒增加 1，LED2 周期 3 s；
- `g_task_hello_count` 每 2 秒增加 1，串口任务周期 2 s；
- `RCC_CSR = 0x00000000`，运行期间没有发生复位；
- PC 在 `0x080001xx`、`0x08001Axx`、`0x08000330` 等地址之间变化，说明任务在正常切换，而不是停在某个死循环。

连续运行约 83 秒后，读取到 `LED1=83、LED2=28、HELLO=42、UART=2320`，仍严格保持 1 s、3 s、2 s 的比例，说明系统长时间运行稳定。`r`n`r`n完整日志见 `Task1_uCOSII/Tools/verify_output.txt` 和 `Task1_uCOSII/Tools/final_check_output.txt`。

### 6.3 USART1 配置与发送内容

运行时读取 USART1 寄存器：

```text
RCC_APB2ENR = 0x00004014   ; USART1EN=1, GPIOAEN=1, AFIOEN=1
GPIOA_CRH   = 0x888444B2   ; PA9 = AF Push-Pull, PA10 = Floating Input
USART1_BRR  = 0x00000271   ; 72 MHz 下 115200 波特率
USART1_CR1  = 0x0000200C   ; UE=1, TE=1, RE=1
USART1_SR   = 0x000000C0   ; TXE=1, TC=1，发送完成
```

从目标 Flash 的 `0x08001D84` 读回字符串：

```text
hello uc/OS! 欢迎来到RTOS多任务环境！
```

对应 UTF-8 字节：

```text
68 65 6C 6C 6F 20 75 63 2F 4F 53 21 20
E6 AC A2 E8 BF 8E E6 9D A5 E5 88 B0
52 54 4F 53 E5 A4 9A E4 BB BB E5 8A A1
E7 8E AF E5 A2 83 EF BC 81 0D 0A
```

说明：

为了确认 `printf` 真的调用 `fputc` 并写入 USART1，在 `fputc` 中增加了 `g_uart_tx_count`，每发送一个字节加 1。实测：

| 时间 | `g_uart_tx_count` | 增量 | 说明 |
|---|---|---|---|
| 1 s | 311 | — | 启动横幅 + 第一条问候 |
| 3 s | 360 | +49 | 第二条问候 |
| 5 s | 409 | +49 | 第三条问候 |

每条问候正好 49 字节：`hello uc/OS! ` 13 字节 + 中文 34 字节（UTF-8）+ CRLF 2 字节，与源码完全一致。这说明串口重定向和 2 s 周期都正确。

- 源文件使用 UTF-8 编码，字符串按 UTF-8 字节写入 Flash；
- `fputc()` 把每个字节写入 USART1->DR；
- `USART1_SR` 的 TXE 和 TC 均为 1，说明数据已经全部移出；
- 上位机串口助手需要选择 **UTF-8** 编码，否则中文会显示为乱码。

### 6.4 关于 BOOT0 的实测说明

烧录和校验都成功，但本机用 DAPLink 复位后发现：

```text
PC = 0x1FFFF3B2
SP = 0x200000C4
SYST_CSR = 0x00000004
SYST_RVR = 524288
```

`0x1FFFFxxx` 是 STM32 系统存储器（System Memory）中的出厂 Bootloader，不是用户 Flash。最常见的原因是当前板子的 **BOOT0 为高电平**（或 BOOT0 被外部复位电路拉高），复位后进入系统 Bootloader，而不是从 `0x08000000` 启动。DAPLink 通过 SWD 烧录不受 BOOT0 影响，所以能烧录、能校验，但程序不会自动运行。

解决方法：

1. 把 BOOT0 跳线从 1 改到 0（接 GND）；
2. 按一下 NRST（或重新上电）；
3. 程序从 `0x08000000` 启动，PC13/PA8 开始闪烁，串口开始输出。

在 BOOT0 未改的情况下，本文的验证是通过 DAPLink 手动把 MSP/PC 设置为向量表中的值（`0x20003450` / `0x08000101`）来启动应用的，仅用于实验台验证；正常使用时必须把 BOOT0 接 0。

## 7. 串口输出与接线

### 7.1 串口参数

| 参数 | 值 |
|---|---|
| 波特率 | 115200 |
| 数据位 | 8 |
| 校验位 | 无 |
| 停止位 | 1 |
| 流控 | 无 |
| 编码 | UTF-8 |

### 7.2 接线

使用 USB-TTL：

```text
USB-TTL RX  → STM32 PA9  (USART1_TX)
USB-TTL TX  → STM32 PA10 (USART1_RX，可选)
USB-TTL GND → STM32 GND
```

如果使用 DAPLink 板上的 USB 转串口，需要确认 DAPLink 的 UART TX/RX 是否已经引到目标板；没有引出时，COM4 收不到数据，需要另接 USB-TTL。

### 7.3 预期输出

```text
==============================================
 STM32F103C8T6 + uC/OS-II 多任务实验（任务一）
 SystemCoreClock = 72000000 Hz, OS_TICKS_PER_SEC = 1000
 LED1: PC13 / 1 s   LED2: PA8 / 3 s   UART: 2 s
==============================================
hello uc/OS! 欢迎来到RTOS多任务环境！
hello uc/OS! 欢迎来到RTOS多任务环境！
hello uc/OS! 欢迎来到RTOS多任务环境！
...
```

第一段是启动横幅，只打印一次；之后每 2 秒打印一行问候语。

## 8. 常见问题与解决

| 现象 | 原因 | 解决方法 |
|---|---|---|
| 编译通过，但程序停在 `0x08000950` 的 `BKPT` | 标准 C 库使用半主机 `_sys_open` | 勾选 `Use MicroLIB`，或重定向 `_sys_open/_sys_write` |
| 烧录报 `No Algorithm found for: 00000000H` | `.sct` 的加载地址是 0，不是 0x08000000 | 修正 IROM/IRAM 和 `OCR_RVCT4/9`，确认 `.sct` 以 `0x08000000` 开头 |
| 烧录成功但复位不运行 | BOOT0=1，进入系统 Bootloader | BOOT0 接 0/GND，按 NRST |
| 只有第一个任务运行 | PendSV 向量没有改成 `OS_CPU_PendSVHandler` | 修改启动文件向量表 |
| 程序死机/ HardFault | 任务堆栈太小、数组越界、`printf` 重入 | 增大堆栈；只在一个任务里 `printf`；检查栈溢出 |
| 串口乱码 | 波特率或编码不对 | 115200-8-N-1，UTF-8；检查 PA9/PA10 是否接反 |
| SysTick 被普通延时占用 | `delay.c` 用 SysTick 做延时 | 改用 DWT 周期计数器做微秒延时 |
| `OSTimeDlyHMSM` 不准确 | `OS_TICKS_PER_SEC` 与 SysTick 配置不一致 | 保持 1000 Hz，`OS_CPU_SysTickInitFreq(SystemCoreClock)` |
| Keil 下载时找不到 DAPLink | 调试器选择错误 | Debug 选 CMSIS-DAP，SWD；Utilities 选 CMSIS-DAP |

## 9. 文件清单

```text
F:\Keil files\AHT20\
├─ Task1_uCOSII\                     Keil 工程
│  ├─ Task1_uCOSII.uvprojx
│  ├─ Task1_uCOSII.uvoptx
│  ├─ CMSIS\                        启动文件、CMSIS、系统时钟
│  ├─ StdPeriph_Driver\             标准外设库
│  ├─ Hardware\
│  │  ├─ led.c / led.h              PC13、PA8
│  │  ├─ usart.c / usart.h          USART1 + fputc
│  │  └─ delay.c / delay.h          DWT 延时
│  ├─ User\
│  │  ├─ main.c                     三个任务
│  │  ├─ app_cfg.h
│  │  ├─ os_cfg.h
│  │  ├─ cpu_cfg.h
│  │  ├─ app_hooks.c
│  │  └─ stm32f10x_conf.h
│  ├─ Middlewares\uC-OS2\           uC/OS-II、uC/CPU、uC/LIB
│  ├─ Objects\
│  │  ├─ Task1_uCOSII.axf
│  │  ├─ Task1_uCOSII.hex
│  │  └─ Task1_uCOSII.bin
│  └─ Tools\
│     ├─ verify_final.py            DAPLink 运行验证脚本
│     ├─ verify_output.txt          10 秒实测日志
│     └─ read_string.py             读取 Flash 中的字符串
├─ 任务一_uCOS-II移植报告.md         本报告
└─ README.md                         工程说明
```

## 10. 复现步骤

1. 用 Keil MDK 打开 `Task1_uCOSII\Task1_uCOSII.uvprojx`。
2. 确认 Device 为 `STM32F103C8`，IROM `0x08000000/0x10000`，IRAM `0x20000000/0x5000`。
3. 确认 `Options for Target → Target → Use MicroLIB` 已勾选。
4. `Project → Rebuild all target files`，应显示 `0 Error(s)`。
5. 确认 `Objects/Task1_uCOSII.sct` 第一行是 `LR_IROM1 0x08000000 0x00010000`。
6. 连接 DAPLink：SWDIO→PA13，SWCLK→PA14，GND→GND，3.3V→3.3V。
7. 把 BOOT0 跳到 0/GND。
8. Keil 中点击 `Download`，或运行 `UV4.exe -f Task1_uCOSII.uvprojx -j0 -o Objects\flash.log`。
9. 按 NRST，观察 PC13 每 1 s 翻转、PA8 每 3 s 翻转。
10. USB-TTL 接 PA9/PA10，115200-8-N-1、UTF-8，观察每 2 s 一行的问候语。

## 11. 结论

本实验完成了 uC/OS-II 在 STM32F103C8T6（Cortex-M3）上的移植，构建了 3 个应用任务：

- `TaskLED1`：1 s 周期翻转 PC13；
- `TaskLED2`：3 s 周期翻转 PA8；
- `TaskHello`：2 s 周期通过 USART1 发送 `hello uc/OS! 欢迎来到RTOS多任务环境！`。

通过 DAPLink 实测：

- SysTick 为 1 ms 节拍（`RVR=71999`）；
- 三个任务的计数分别以 1 s、3 s、2 s 的速率增加；
- GPIO 输出与任务周期一致；
- USART1 配置为 115200，发送完成标志 TC=1；
- Flash 中的 UTF-8 字符串与要求完全一致。

同时记录了移植中的关键问题：PendSV 向量、SysTick 初始化、临界区、堆栈方向、半主机 `BKPT`、Flash 起始地址和 BOOT0 启动模式。通过本实验，掌握了 RTOS 在 Cortex-M3 上的移植方法和多任务调试方法。