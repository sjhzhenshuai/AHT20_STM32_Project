# 任务二：AHT20 温湿度采集（uC/OS-II 三任务）

本目录是任务二(3)的工程：在任务一基础上，把第 3 个任务改为每 2 秒采集一次 AHT20，
温湿度通过 USART1 发送到上位机。

## 已烧录

`Task2_AHT20/Objects/Task2_AHT20.hex`（已通过 DAPLink 烧录并校验通过）

| 任务 | 优先级 | 周期 | 功能 |
|---|---|---|---|
| `TaskLED1` | 5 | 1 s | 翻转 PC13 板载 LED |
| `TaskLED2` | 6 | 3 s | 翻转 PA8 外接 LED |
| `TaskAHT20` | 7 | 2 s | 采集 AHT20 并串口输出温湿度 |

## 接线

```text
AHT20 ：VCC → 3.3V，GND → GND，SCL → PB6，SDA → PB7（软件 I2C）
USART1：PA9(TX) → USB-TTL RX，PA10(RX) → USB-TTL TX，GND 共地
DAPLink：SWDIO→PA13，SWCLK→PA14，GND→GND，3.3V→3.3V
BOOT0 ：接 0/GND
```

串口参数：`115200-8-N-1`，编码 `UTF-8`。
若 AHT20 模块不带 4.7k 上拉电阻，需要在 SCL/SDA 上各外接一个 4.7kΩ 到 3.3V。

## 上电输出

```text
==============================================
 STM32F103C8T6 + uC/OS-II + AHT20（任务二）
 I2C: software bit-bang, SCL=PB6, SDA=PB7
==============================================
I2C scan (PB6=SCL, PB7=SDA):
  found device at 0x38
[AHT20] init OK (addr 0x38)
[1] AHT20: T=25.34 C, RH=48.21 %  (CRC OK)
[2] AHT20: T=25.35 C, RH=48.20 %  (CRC OK)
```

看到 `found device at 0x38` 说明 AHT20 接线、上拉、供电都正常。
串口无输出时先检查 USB-TTL 是否枚举成 COM 口、TX/RX 是否交叉、GND 是否共地。

## 代码结构

```text
Task2_AHT20/          Keil 工程（CMSIS、StdPeriph、uC/OS-II、User）
Common/aht20.c/.h     AHT20 命令、CRC、温湿度换算
Common/i2c_soft.c     PB6/PB7 软件模拟 I2C（默认）
Common/i2c_hw.c       STM32 硬件 I2C1（把 Common/i2c.h 中 AHT20_USE_HW_I2C 改为 1）
Common/i2c.c/.h       总线接口与地址扫描
```

## 编译与烧录

Keil 打开 `Task2_AHT20/Task2_AHT20.uvprojx`，Rebuild 后 Download。
命令行：

```text
UV4.exe -b Task2_AHT20.uvprojx -j0 -o build.log
UV4.exe -f Task2_AHT20.uvprojx -j0 -o flash.log
```
