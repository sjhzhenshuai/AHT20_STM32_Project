import re, pathlib
s=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md").read_text(encoding="utf-8")
# find image and video links in document order
pat=re.compile(r"!\[[^\]]*\]\(media/(\d+)\.|\[[^\]]*视频[^\]]*\]\(media/(\d+)\.mp4\)")
nums=[]
for m in pat.finditer(s):
    nums.append(int(m.group(1) or m.group(2)))
print(nums); print(len(nums),nums==list(range(1,41)))
print("pagebreak",s.count("<!-- pagebreak -->"))