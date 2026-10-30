#ifndef __I2C_H
#define __I2C_H

#include "stm32f10x.h"

/*
 * I2C 总线抽象层（AHT20 使用）
 *
 * 两种实现共用同一套接口，接线也相同：PB6 = SCL，PB7 = SDA。
 *   AHT20_USE_HW_I2C = 0 ：软件模拟 I2C（GPIO 翻转，默认）
 *   AHT20_USE_HW_I2C = 1 ：STM32 硬件 I2C1
 *
 * 返回值：0 = 成功；1 = 从机 NACK；2 = 总线错误/超时
 */
#ifndef AHT20_USE_HW_I2C
#define AHT20_USE_HW_I2C    0
#endif

void    I2C_BusInit(void);
uint8_t I2C_Write(uint8_t dev_addr, const uint8_t *data, uint16_t len);
uint8_t I2C_Read(uint8_t dev_addr, uint8_t *data, uint16_t len);
uint8_t I2C_Probe(uint8_t dev_addr);

/* 扫描 0x08~0x77 并在串口打印在线地址，用于检查接线 */
void    I2C_BusScan(void);

#endif
