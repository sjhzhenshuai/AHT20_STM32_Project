from pyocd.core.helpers import ConnectHelper
with ConnectHelper.session_with_chosen_probe(target_override="stm32f103rc", options={"connect_mode":"attach"}) as s:
    t=s.target; t.halt()
    print("PC=0x%08X" % t.read_core_register("pc"))
    print("SYST_CSR=0x%08X SYST_RVR=%d" % (t.read32(0xE000E010), t.read32(0xE000E014)))
    print("counts L1=%d L2=%d HELLO=%d UART=%d" % (t.read32(0x20003040), t.read32(0x20003044), t.read32(0x2000303C), t.read32(0x20003048)))
    print("USART1 SR=0x%08X BRR=0x%08X CR1=0x%08X" % (t.read32(0x40013800), t.read32(0x40013808), t.read32(0x4001380C)))
    t.resume()