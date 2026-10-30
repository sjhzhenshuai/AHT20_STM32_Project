import re, pathlib
s=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8")
refs=re.findall(r"!img media/(\d+)\.",s)+re.findall(r"!video media/(\d+)\.",s)
nums=[int(x) for x in refs]
print("markers",len(nums)); print(nums); print("missing",[i for i in range(1,41) if i not in nums]); print("dups",[i for i in set(nums) if nums.count(i)>1])
print("in order", nums==list(range(1,41)))