import re,pathlib
s=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8")
nums=[int(m.group(1)) for m in re.finditer(r"\]\(media/(\d+)\.",s)]
print("media refs",len(nums),"order",nums==list(range(1,41)))
print("old markers",s.count("!img "),s.count("!video "),s.count("!pagebreak"))
print("chars",len(s))