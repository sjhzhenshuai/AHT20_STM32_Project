#ifndef __USART_H
#define __USART_H
#include "stm32f10x.h"
#include <stdio.h>

void USART1_Init(uint32_t baudrate);

extern volatile uint32_t g_uart_tx_count;

#endif
