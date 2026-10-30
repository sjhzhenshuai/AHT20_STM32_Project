#ifndef __AHT20_H
#define __AHT20_H

#include "stm32f10x.h"

/* AHT20 温湿度传感器：7 位 I2C 地址 0x38（写 0x70 / 读 0x71） */
#define AHT20_I2C_ADDR      0x38u

#define AHT20_OK            0u
#define AHT20_ERR_NACK      1u
#define AHT20_ERR_TIMEOUT   2u
#define AHT20_ERR_NOT_READY 3u

typedef struct {
    float   temperature;    /* 摄氏度 */
    float   humidity;       /* 相对湿度 %RH */
    uint8_t crc_ok;         /* 1 = CRC 校验通过 */
} AHT20_Data;

/* 上电初始化：发送 0xBE 0x08 0x00 并等待校准完成 */
uint8_t AHT20_Init(void);

/* 触发一次测量并读取温湿度，返回值 0 表示成功 */
uint8_t AHT20_Read(AHT20_Data *out);

/* 读取 7 字节原始数据：状态 + 5 字节数据 + CRC */
uint8_t AHT20_ReadRaw(uint8_t raw[7]);

const char *AHT20_ErrString(uint8_t err);

#endif
