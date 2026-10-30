from pyocd.core.helpers import ConnectHelper
with ConnectHelper.session_with_chosen_probe(target_override="stm32f103rc", options={"connect_mode":"attach"}) as s:
    t=s.target; t.halt()
    data=bytes(t.read_memory_block8(0x08001D84, 80))
    end=data.find(b"\x00")
    print("vector:", [hex(x) for x in t.read_memory_block32(0x08000000, 2)])
    print("raw:", data[:end])
    print("utf8:", data[:end].decode("utf-8", errors="replace"))
    t.resume()