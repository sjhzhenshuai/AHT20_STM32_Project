import re,pathlib
p=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md")
s=p.read_text(encoding="utf-8")
nums=[int(x) for x in re.findall(r"!\[[^\]]*\]\(media/(\d+)\.|\[[^\]]*视频[^\]]*\]\(media/(\d+)\.mp4\)",s) for x in [x if isinstance(x,str) else x]]
# simpler combined
nums=[]
for m in re.finditer(r"!\[[^\]]*\]\(media/(\d+)\.|\[[^\]]*视频[^\]]*\]\(media/(\d+)\.mp4\)",s):
    nums.append(int(m.group(1) or m.group(2)))
print("media refs",len(nums),"order",nums==list(range(1,41)))
print("old markers", s.count("!img "), s.count("!video "), s.count("!pagebreak"))
print("chars",len(s))