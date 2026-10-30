import re, pathlib
s=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8")
nums=[int(x) for x in re.findall(r"!(?:img|video) media/(\d+)\.",s)]
print(nums); print("count",len(nums),"in order",nums==list(range(1,41)))