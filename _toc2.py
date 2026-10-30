import pathlib
lines=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8").splitlines()
for i in range(12,43): print(i+1,repr(lines[i]))