import time
from pyocd.core.helpers import ConnectHelper

TARGET="stm32f103rc"
C_HELLO=0x2000303C
C_LED1=0x20003040
C_LED2=0x20003044
C_UART=0x20003048
USART1_SR=0x40013800
USART1_BRR=0x40013808
USART1_CR1=0x4001380C
GPIOA_CRH=0x40010804

with ConnectHelper.session_with_chosen_probe(target_override=TARGET, options={"connect_mode":"attach"}) as s:
    t=s.target
    t.reset_and_halt()
    msp=t.read32(0x08000000); reset=t.read32(0x08000004)
    t.write_core_register("msp",msp); t.write_core_register("pc",reset); t.resume()
    print(f"started, vector MSP=0x{msp:08X} reset=0x{reset:08X}")
    prev=None
    for i in range(6):
        time.sleep(1.0)
        t.halt()
        h=t.read32(C_HELLO); l1=t.read32(C_LED1); l2=t.read32(C_LED2); u=t.read32(C_UART)
        sr=t.read32(USART1_SR); brr=t.read32(USART1_BRR); cr1=t.read32(USART1_CR1); crh=t.read32(GPIOA_CRH)
        d="" if prev is None else f"  d_uart={u-prev:+d}"
        print(f"t={i+1}s hello={h} led1={l1} led2={l2} uart_bytes={u}{d}")
        if i==0:
            print(f"  USART1_SR=0x{sr:08X} BRR=0x{brr:08X} CR1=0x{cr1:08X} GPIOA_CRH=0x{crh:08X}")
        prev=u
        t.resume()