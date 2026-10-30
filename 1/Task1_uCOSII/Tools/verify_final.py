"""Final Task 1 verification: run the image and sample task counters.

The STM32F103 on the bench currently has BOOT0 high, so a normal reset enters
the system bootloader.  For bench verification we reset, then set MSP/PC from
the image vector table to start the application.  In normal use BOOT0 must be
low so the chip boots from flash directly.
"""

import time

from pyocd.core.helpers import ConnectHelper

TARGET = "stm32f103rc"
GPIOA_ODR = 0x4001080C
GPIOC_ODR = 0x4001100C
SYST_CSR = 0xE000E010
SYST_RVR = 0xE000E014
RCC_CSR = 0x40021024
C_HELLO = 0x2000303C
C_LED1 = 0x20003040
C_LED2 = 0x20003044


def main():
    with ConnectHelper.session_with_chosen_probe(
        target_override=TARGET, options={"connect_mode": "attach"}
    ) as session:
        target = session.target
        target.reset_and_halt()
        msp = target.read32(0x08000000)
        reset = target.read32(0x08000004)
        print(f"vector table: MSP=0x{msp:08X}  Reset_Handler=0x{reset:08X}")
        target.write32(RCC_CSR, 0x01000000)
        target.write_core_register("msp", msp)
        target.write_core_register("pc", reset)
        target.resume()
        print("application started; sampling every 0.5 s\n")

        prev = None
        for i in range(20):
            time.sleep(0.5)
            target.halt()
            hello = target.read32(C_HELLO)
            led1 = target.read32(C_LED1)
            led2 = target.read32(C_LED2)
            pc = target.read_core_register("pc")
            a = target.read32(GPIOA_ODR)
            c = target.read32(GPIOC_ODR)
            csr = target.read32(SYST_CSR)
            rvr = target.read32(SYST_RVR)
            rcc = target.read32(RCC_CSR)
            delta = "" if prev is None else f"  d=({led1-prev[0]:+d},{led2-prev[1]:+d},{hello-prev[2]:+d})"
            print(
                f"t={(i + 1) * 0.5:04.1f}s  PC=0x{pc:08X}  "
                f"counts(LED1,LED2,HELLO)=({led1},{led2},{hello}){delta}  "
                f"PA8={'ON' if a & (1 << 8) else 'OFF'} "
                f"PC13={'ON' if not (c & (1 << 13)) else 'OFF'}  "
                f"SYST_CSR=0x{csr:08X} RVR={rvr} RCC_CSR=0x{rcc:08X}"
            )
            prev = (led1, led2, hello)
            target.resume()

        print(
            f"\nsummary: LED1={led1} toggles, LED2={led2} toggles, "
            f"HELLO={hello} messages in about 10 s"
        )


if __name__ == "__main__":
    main()