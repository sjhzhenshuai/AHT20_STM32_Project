import pathlib
lines=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8").splitlines()
for i,l in enumerate(lines[:90],1):
    if 30<=i<=75: print(i,repr(l))