from pathlib import Path
from PIL import Image
media=Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\media")
files=sorted(media.iterdir(), key=lambda p:int(p.stem))
print("count",len(files))
for p in files:
    if p.suffix.lower()==".mp4":
        print(p.name, p.stat().st_size)
    else:
        im=Image.open(p); print(p.name, im.size, im.format, p.stat().st_size)