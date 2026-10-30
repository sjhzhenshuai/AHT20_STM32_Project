#include "aht20.h"
#include "i2c.h"
#include "delay.h"

/* AHT20 命令（见 AHT20 产品手册）：
 *   0xBE 0x08 0x00 : 初始化/校准，状态寄存器 bit3 置 1 表示校准完成
 *   0xAC 0x33 0x00 : 触发一次温湿度测量，等待约 80 ms 后读取
 *   0xBA           : 软复位（本例未使用）
 * 读取 7 字节：状态(1) + 湿度(2.5) + 温度(2.5) + CRC(1)
 */

#define AHT20_CMD_INIT0     0xBEu
#define AHT20_CMD_INIT1     0x08u
#define AHT20_CMD_INIT2     0x00u
#define AHT20_CMD_TRIG0     0xACu
#define AHT20_CMD_TRIG1     0x33u
#define AHT20_CMD_TRIG2     0x00u

#define AHT20_STATUS_BUSY   0x80u
#define AHT20_STATUS_CAL    0x08u

/* CRC-8：多项式 0x31，初值 0xFF，覆盖前 6 字节 */
static uint8_t aht20_crc8(const uint8_t *data, uint8_t len)
{
    uint8_t crc = 0xFFu;
    uint8_t i;

    while (len-- != 0u) {
        crc ^= *data++;
        for (i = 0u; i < 8u; i++) {
            if ((crc & 0x80u) != 0u) {
                crc = (uint8_t)((crc << 1) ^ 0x31u);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

uint8_t AHT20_Init(void)
{
    static const uint8_t init_cmd[3] = {
        AHT20_CMD_INIT0, AHT20_CMD_INIT1, AHT20_CMD_INIT2
    };
    uint8_t status;
    uint8_t err;
    uint8_t i;

    delay_ms(100);              /* 上电稳定时间，手册要求 >= 100 ms */
    I2C_BusInit();

    for (i = 0u; i < 3u; i++) {
        err = I2C_Write(AHT20_I2C_ADDR, init_cmd, 3u);
        if (err != 0u) {
            return err;         /* 1 = 地址/数据 NACK，检查接线 */
        }
        delay_ms(10);

        err = I2C_Read(AHT20_I2C_ADDR, &status, 1u);
        if (err != 0u) {
            return err;
        }
        if (((status & AHT20_STATUS_CAL) != 0u) &&
            ((status & AHT20_STATUS_BUSY) == 0u)) {
            return AHT20_OK;    /* 已校准且空闲 */
        }
        delay_ms(10);
    }

    return AHT20_ERR_NOT_READY;
}

uint8_t AHT20_ReadRaw(uint8_t raw[7])
{
    static const uint8_t trig_cmd[3] = {
        AHT20_CMD_TRIG0, AHT20_CMD_TRIG1, AHT20_CMD_TRIG2
    };
    uint8_t err;
    uint8_t retry;

    for (retry = 0u; retry < 3u; retry++) {
        err = I2C_Write(AHT20_I2C_ADDR, trig_cmd, 3u);
        if (err != 0u) {
            return err;
        }

        delay_ms(80);           /* 转换时间，手册典型值 80 ms */

        err = I2C_Read(AHT20_I2C_ADDR, raw, 7u);
        if (err != 0u) {
            return err;
        }
        if ((raw[0] & AHT20_STATUS_BUSY) == 0u) {
            return AHT20_OK;
        }
        delay_ms(10);
    }

    return AHT20_ERR_NOT_READY;
}

uint8_t AHT20_Read(AHT20_Data *out)
{
    uint8_t raw[7];
    uint32_t hum_raw;
    uint32_t temp_raw;
    uint8_t err;

    if (out == 0) {
        return AHT20_ERR_NACK;
    }

    err = AHT20_ReadRaw(raw);
    if (err != AHT20_OK) {
        return err;
    }

    /* 20 bit 湿度 + 20 bit 温度，共 5 字节，第 3 字节高低半字节分属两者 */
    hum_raw  = ((uint32_t)raw[1] << 12) |
               ((uint32_t)raw[2] << 4)  |
               ((uint32_t)raw[3] >> 4);
    temp_raw = (((uint32_t)raw[3] & 0x0Fu) << 16) |
               ((uint32_t)raw[4] << 8) |
               ((uint32_t)raw[5]);

    out->humidity    = (float)hum_raw * 100.0f / 1048576.0f;
    out->temperature = (float)temp_raw * 200.0f / 1048576.0f - 50.0f;
    out->crc_ok      = (aht20_crc8(raw, 6u) == raw[6]) ? 1u : 0u;

    return AHT20_OK;
}

const char *AHT20_ErrString(uint8_t err)
{
    switch (err) {
    case AHT20_OK:            return "OK";
    case AHT20_ERR_NACK:      return "NACK (check wiring/address)";
    case AHT20_ERR_TIMEOUT:   return "bus timeout";
    case AHT20_ERR_NOT_READY: return "not calibrated/busy";
    default:                  return "unknown";
    }
}
