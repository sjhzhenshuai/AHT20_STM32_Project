import pathlib
p=pathlib.Path(r"F:\Keil files\AHT20\1\Task1_uCOSII\User\main.c")
lines=p.read_text(encoding="utf-8").splitlines()
print("count",len(lines))
for i,l in enumerate(lines,1):
    if any(k in l for k in ["#include \"stm32f10x.h\"","TASK_LED1_PRIO","static void TaskLED1","static void TaskHello","int main","OSStart"]): print(i,l)