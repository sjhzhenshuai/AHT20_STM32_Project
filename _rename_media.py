from pathlib import Path
import shutil
root=Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4")
t1=root/"任务1"/"任务一实验结果截图"
t2=root/"任务2"/"任务二实验结果截图"
media=root/"media"
media.mkdir(exist_ok=True)
items=[
 (1,t1/"c53cae8d599562b9ea9dcef5819613d8.png","1.jpg"),
 (2,t1/"22a99ba2820bd84e3fa1f691e1431b92.png","2.jpg"),
 (3,t1/"a2991a0c9fcace3b84a69fb7bc5fab03.png","3.jpg"),
 (4,t1/"bec44271e983b0186de14e364348e58b.mp4","4.mp4"),
 (5,t1/"01_main_任务优先级与三个任务.png","5.png"),
 (6,t1/"02_main_任务创建与调度启动.png","6.png"),
 (7,t1/"05_os_cfg.h_内核关键配置.png","7.png"),
 (8,t1/"06_cpu_cfg.h_CPU与临界区配置.png","8.png"),
 (9,t1/"07_app_cfg.h_应用配置.png","9.png"),
 (10,t1/"08_startup_PendSV向量表.png","10.png"),
 (11,t1/"09_os_cpu_a_PendSV上下文切换.png","11.png"),
 (12,t1/"10_os_cpu_c_SysTick节拍.png","12.png"),
 (13,t1/"03_led.c_LED驱动.png","13.png"),
 (14,t1/"04_usart.c_USART初始化与printf重定向.png","14.png"),
 (15,t1/"11_delay.c_DWT延时.png","15.png"),
 (16,t1/"屏幕截图 2026-10-30 140427.png","16.png"),
 (17,t1/"XCOM_115200_COM4_等待串口接线.png","17.png"),
 (19,t2/"01_main_工程配置与任务优先级.png","19.png"),
 (20,t2/"02_main_三个任务函数.png","20.png"),
 (21,t2/"03_main_初始化与任务创建.png","21.png"),
 (22,t2/"06_i2c_soft.c_GPIO与总线初始化.png","22.png"),
 (23,t2/"07_i2c_soft.c_起始与停止时序.png","23.png"),
 (24,t2/"08_i2c_soft.c_字节收发与ACK.png","24.png"),
 (25,t2/"09_i2c_soft.c_读写与探测.png","25.png"),
 (26,t2/"10_i2c.c_总线地址扫描.png","26.png"),
 (27,t2/"11_i2c.h_软件硬件I2C切换.png","27.png"),
 (28,t2/"12_i2c_hw.c_硬件I2C初始化.png","28.png"),
 (29,t2/"13_aht20.h_地址与接口.png","29.png"),
 (30,t2/"04_aht20.c_初始化命令与CRC.png","30.png"),
 (31,t2/"05_aht20.c_读取与温湿度换算.png","31.png"),
 (32,t2/"屏幕截图 2026-10-28 130340.png","32.png"),
 (33,t2/"屏幕截图 2026-10-28 130517.png","33.png"),
 (34,t2/"屏幕截图 2026-10-28 130612.png","34.png"),
 (35,t2/"屏幕截图 2026-10-28 130710.png","35.png"),
 (36,t2/"屏幕截图 2026-10-28 131556.png","36.png"),
 (37,t2/"屏幕截图 2026-10-28 131610.png","37.png"),
 (38,t2/"屏幕截图 2026-10-30 143126.png","38.png"),
 (39,t2/"用手握一段时间后的温度.png","39.png"),
 (40,t2/"现实温度.png","40.jpg"),
]
missing=[str(s) for _,s,_ in items if not s.exists()]
if missing:
    print("MISSING:")
    for m in missing: print(m)
    raise SystemExit(1)
for n,s,d in items:
    dst=media/d
    if dst.exists():
        print("TARGET EXISTS",dst); raise SystemExit(1)
for n,s,d in items:
    dst=media/d
    if d.lower().endswith(".jpg"):
        shutil.copy2(s,dst); s.unlink()
    else:
        shutil.move(str(s),str(dst))
    print(f"{n:02d} <- {s.name}")
# remove stale indexes
for p in [t1/"代码截图目录.txt",t2/"代码截图目录.txt"]:
    if p.exists(): p.unlink()
print("DONE", len(items), "files ->", media)