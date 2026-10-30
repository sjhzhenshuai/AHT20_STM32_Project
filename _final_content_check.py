import re,pathlib
root=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4")
md=(root/"实验4_综合实验报告.md").read_text(encoding="utf-8")
nums=[int(m.group(1)) for m in re.finditer(r"\]\(media/(\d+)\.",md)]
print("MD media links:",len(nums),"order:",nums==list(range(1,41)))
print("MD chars:",len(md),"old markers:",md.count("!img "),md.count("!video "))
print("media files:",len(list((root/"media").iterdir())))
print("AI record:", (root/"AI对话记录.md").exists(), (root/"AI对话记录.md").stat().st_size)
print("zip:", (root/"项目源码.zip").stat().st_size)