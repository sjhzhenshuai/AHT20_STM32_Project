import re, pathlib
p=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md")
s=p.read_text(encoding="utf-8")
refs=re.findall(r"media/(\d+)\.(?:png|jpg|mp4)",s)
nums=[int(x) for x in refs]
print("refs",len(nums),"unique",len(set(nums)))
print("order",nums)
print("missing",[i for i in range(1,41) if i not in nums])
print("dups",[i for i in set(nums) if nums.count(i)>1])
print("first20",nums[:20]); print("last10",nums[-10:])
print("chars",len(s))