# STM32F103C8T6 uC/OS-II 实验（任务一）

本目录包含任务一：把 uC/OS-II 移植到 STM32F103C8T6，并运行 3 个任务。

## 目录

| 路径 | 内容 |
|---|---|
| `Task1_uCOSII/` | Keil MDK 工程（源码、uC/OS-II、编译输出） |
| `Task1_uCOSII/Task1_uCOSII.uvprojx` | 双击打开的 Keil 工程 |
| `Task1_uCOSII/Objects/Task1_uCOSII.hex` | 可直接烧录的 HEX |
| `Task1_uCOSII/Objects/Task1_uCOSII.bin` | 可直接烧录的 BIN |
| `Task1_uCOSII/Tools/verify_output.txt` | 10 秒实测日志（任务计数、SysTick、GPIO） |
| `Task1_uCOSII/Tools/verify_uart_output.txt` | 串口发送字节数实测日志 |
| `Task1_uCOSII/Tools/final_check_output.txt` | 长时间运行后的最终计数 |
| `任务一_uCOS-II移植报告.md` | 详细移植报告 |

## 三个任务

| 任务 | 优先级 | 周期 | 功能 |
|---|---|---|---|
| `TaskLED1` | 5 | 1 s | 翻转 PC13 板载 LED |
| `TaskLED2` | 6 | 3 s | 翻转 PA8 外接 LED |
| `TaskHello` | 7 | 2 s | USART1 发送 `hello uc/OS! 欢迎来到RTOS多任务环境！` |

## 接线

```text
LED1：PC13（板载，低电平点亮）
LED2：PA8 → 220Ω~1kΩ → LED → GND（高电平点亮）
USART1：PA9(TX) → USB-TTL RX；PA10(RX) → USB-TTL TX；GND 共地
DAPLink：SWDIO→PA13，SWCLK→PA14，GND→GND，3.3V→3.3V
BOOT0：必须接 0/GND
```

串口参数：`115200-8-N-1`，编码 `UTF-8`。

## 编译与烧录

1. Keil 打开 `Task1_uCOSII/Task1_uCOSII.uvprojx`。
2. 确认 `Options for Target → Target → Use MicroLIB` 已勾选。
3. `Project → Rebuild all target files`，应为 `0 Error(s)`。
4. 确认 `Objects/Task1_uCOSII.sct` 第一行是 `LR_IROM1 0x08000000 0x00010000`。
5. DAPLink 选 `CMSIS-DAP Debugger`、SWD，Utilities 选 `Use Target Driver for Flash Programming`。
6. 把 BOOT0 跳到 0/GND，点击 `Download`，按 NRST。
7. 观察 PC13 每 1 s 翻转、PA8 每 3 s 翻转；串口每 2 s 输出一行。

命令行烧录：

```text
UV4.exe -f Task1_uCOSII.uvprojx -j0 -o Objects\flash.log
```

## 重要说明：BOOT0

本机实测发现，当前板子复位后 PC 停在 `0x1FFFF3B2`，即 STM32 系统 Bootloader；最常见的原因是板子的 **BOOT0 为高**（或被外部复位电路拉高）。DAPLink 仍能通过 SWD 烧录和校验，但程序不会自动从 Flash 启动。

请把 BOOT0 跳线改到 0（GND）后按 NRST，程序才会从 `0x08000000` 启动。报告 6.4 节记录了该现象和验证方法。

## 实测结果

- 向量表：`0x08000000 = 0x20003450`，`0x08000004 = 0x08000101`
- SysTick：`CSR=0x00010007`，`RVR=71999`（1 ms 节拍）
- 10 秒计数：LED1 11 次（1/s）、LED2 4 次（1/3s）、HELLO 5 次（1/2s）
- USART1：`BRR=0x271`（115200），`CR1=0x200C`，`SR=0xC0`（TXE/TC）
- 串口实测：`g_uart_tx_count` 启动后为 311 字节，之后每 2 s 增加 49 字节（一条问候语），证明 `printf` 已重定向到 USART1
- Flash 字符串 `0x08001D84` 读回与要求完全一致（UTF-8）

## 任务二

任务二（AHT20 温湿度采集、软件/硬件 I2C、示波器时序分析）将在任务一工程基础上继续完成，目前本目录只包含任务一。