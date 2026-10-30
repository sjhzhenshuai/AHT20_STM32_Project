#include "i2c.h"
#include <stdio.h>

/* 总线扫描：逐个地址发 START + 地址字节 + STOP，
 * 收到 ACK 说明该 7 位地址上有从机。 */
void I2C_BusScan(void)
{
    uint8_t addr;
    uint8_t found = 0u;

    printf("I2C scan (PB6=SCL, PB7=SDA):\r\n");
    for (addr = 0x08u; addr <= 0x77u; addr++) {
        if (I2C_Probe(addr) == 0u) {
            printf("  found device at 0x%02X\r\n", (unsigned int)addr);
            found++;
        }
    }
    if (found == 0u) {
        printf("  no I2C device found, check VCC/GND/SCL/SDA and pull-ups\r\n");
    }
}
