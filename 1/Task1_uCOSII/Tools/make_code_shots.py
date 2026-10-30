# -*- coding: utf-8 -*-
"""Generate syntax-highlighted code screenshots for the Task 1 lab report."""

import html
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CLexer, NasmLexer

BASE = Path(r"F:\Keil files\AHT20\1\Task1_uCOSII")
OUT = Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\任务1\任务一实验结果截图")
TMP = Path(r"F:\Keil files\AHT20\_code_shots_html")
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

SPECS = [
    ("01_main_任务优先级与三个任务.png", r"User\main.c", 18, 86,
     "User/main.c — 任务优先级与三个任务", "STM32F103C8T6 + uC/OS-II 任务一 · 第 18–86 行"),
    ("02_main_任务创建与调度启动.png", r"User\main.c", 88, 133,
     "User/main.c — 任务创建与调度启动", "STM32F103C8T6 + uC/OS-II 任务一 · 第 88–133 行"),
    ("03_led.c_LED驱动.png", r"Hardware\led.c", 1, 30,
     "Hardware/led.c — LED 驱动", "PC13 板载 LED（低电平点亮） / PA8 外接 LED（高电平点亮）"),
    ("04_usart.c_USART初始化与printf重定向.png", r"Hardware\usart.c", 1, 44,
     "Hardware/usart.c — USART1 初始化与 printf 重定向", "PA9(TX) / PA10(RX)，115200-8-N-1"),
    ("05_os_cfg.h_内核关键配置.png", r"User\os_cfg.h", 34, 76,
     "User/os_cfg.h — uC/OS-II 内核关键配置", "1 ms 节拍 / 64 个优先级 / 统计任务"),
    ("06_cpu_cfg.h_CPU与临界区配置.png", r"User\cpu_cfg.h", 1, 13,
     "User/cpu_cfg.h — CPU 与临界区配置", "BASEPRI 临界区：KA_IPL_BOUNDARY = 1，NVIC_PRIO_BITS = 4"),
    ("07_app_cfg.h_应用配置.png", r"User\app_cfg.h", 53, 66,
     "User/app_cfg.h — 应用配置", "启动任务优先级、定时器任务优先级与堆栈大小"),
    ("08_startup_PendSV向量表.png", r"CMSIS\startup_stm32f10x_md.s", 55, 80,
     "startup_stm32f10x_md.s — PendSV 向量表", "将默认 PendSV_Handler 改为 OS_CPU_PendSVHandler"),
    ("09_os_cpu_a_PendSV上下文切换.png",
     r"Middlewares\uC-OS2\uC-OS2\Ports\ARM-Cortex-M\ARMv7-M\ARM\os_cpu_a.asm", 329, 369,
     "os_cpu_a.asm — PendSV 上下文切换", "保存 R4–R11/R14、切换 PSP 与 TCB、异常返回"),
    ("10_os_cpu_c_SysTick节拍.png",
     r"Middlewares\uC-OS2\uC-OS2\Ports\ARM-Cortex-M\ARMv7-M\os_cpu_c.c", 650, 690,
     "os_cpu_c.c — SysTick 节拍", "OS_CPU_SysTickHandler() 与 OS_CPU_SysTickInitFreq()"),
    ("11_delay.c_DWT延时.png", r"Hardware\delay.c", 1, 26,
     "Hardware/delay.c — DWT 微秒延时", "RTOS 占用 SysTick 后，软件 I2C 的短延时改用 DWT"),
]

CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: #eef2f7;
  padding: 28px;
  font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}
.page {
  width: 1240px;
  margin: 0 auto;
  background: #ffffff;
  border: 1px solid #d8dee6;
  border-radius: 10px;
  box-shadow: 0 8px 28px rgba(20, 40, 70, 0.10);
  overflow: hidden;
}
.header {
  background: #1f3a5f;
  color: #ffffff;
  padding: 18px 26px 17px 26px;
}
.title { font-size: 24px; font-weight: 700; letter-spacing: 0.3px; }
.subtitle { margin-top: 5px; font-size: 13px; color: #c9d6e8; }
.code-card { padding: 18px 22px 20px 22px; }
.footer {
  padding: 0 26px 16px 26px;
  color: #6b7785;
  font-size: 12px;
  font-family: Consolas, "Cascadia Mono", monospace;
}
.codehilite {
  background: #fbfcfe !important;
  border: 1px solid #e1e6ed;
  border-radius: 6px;
  padding: 14px 16px;
  overflow: visible;
}
.codehilite table { border-spacing: 0; border-collapse: collapse; width: 100%; }
.codehilite td { vertical-align: top; }
.codehilite pre {
  margin: 0;
  font-family: Consolas, "Cascadia Mono", "Microsoft YaHei", monospace;
  font-size: 14px;
  line-height: 1.62;
  white-space: pre;
}
.codehilite .linenos {
  color: #8c959f;
  padding-right: 14px;
  border-right: 1px solid #e1e6ed;
  text-align: right;
  user-select: none;
}
.codehilite .linenos pre { color: #8c959f; font-size: 14px; line-height: 1.62; }
.codehilite .code { padding-left: 14px; }
"""


def build_html(src: Path, start: int, end: int, title: str, subtitle: str) -> str:
    lines = src.read_text(encoding="utf-8").splitlines()
    code = "\n".join(lines[start - 1:end])
    lexer = CLexer() if src.suffix.lower() in (".c", ".h") else NasmLexer()
    formatter = HtmlFormatter(
        style="friendly",
        linenos="table",
        linenostart=start,
        cssclass="codehilite",
    )
    body = highlight(code, lexer, formatter)
    style_defs = formatter.get_style_defs(".codehilite")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}\n{style_defs}</style></head>
<body><div class="page">
  <div class="header">
    <div class="title">{html.escape(title)}</div>
    <div class="subtitle">{html.escape(subtitle)}</div>
  </div>
  <div class="code-card">{body}</div>
  <div class="footer">{html.escape(str(src))}</div>
</div></body></html>"""


def crop_bottom(path: Path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    bg = (238, 242, 247)
    last = h - 1
    for y in range(h - 1, -1, -1):
        hit = False
        for x in range(0, w, 8):
            p = img.getpixel((x, y))
            if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 14:
                hit = True
                break
        if hit:
            last = y
            break
    new_h = min(h, last + 42)
    if new_h < h:
        img.crop((0, 0, w, new_h)).save(path, "PNG")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="edge_", dir=str(TMP)))

    for idx, (name, rel, start, end, title, subtitle) in enumerate(SPECS, 1):
        src = BASE / rel
        if not src.exists():
            raise FileNotFoundError(src)
        total = len(src.read_text(encoding="utf-8").splitlines())
        if end > total:
            raise ValueError(f"{src}: end {end} > {total}")
        html_path = TMP / f"{idx:02d}.html"
        png_tmp = TMP / f"{idx:02d}.png"
        html_path.write_text(build_html(src, start, end, title, subtitle), encoding="utf-8")
        n = end - start + 1
        height = max(720, 250 + int(n * 24.2))
        cmd = [
            str(EDGE),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",
            "--force-device-scale-factor=2",
            f"--window-size=1320,{height}",
            f"--screenshot={png_tmp}",
            html_path.as_uri(),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if not png_tmp.exists():
            raise RuntimeError(f"Edge screenshot failed: {name}")
        crop_bottom(png_tmp)
        final = OUT / name
        shutil.move(str(png_tmp), str(final))
        print(f"OK {name}  ({n} lines)")

    shutil.rmtree(profile, ignore_errors=True)
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()