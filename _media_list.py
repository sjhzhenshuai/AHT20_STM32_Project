from pathlib import Path
from PIL import Image
root=Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4")
for p in sorted(root.rglob("*")):
    if p.suffix.lower() in (".png",".jpg",".jpeg",".mp4"):
        try:
            if p.suffix.lower()==".mp4":
                print(f"VIDEO {p.relative_to(root)} {p.stat().st_size}")
            else:
                im=Image.open(p)
                print(f"IMG {p.relative_to(root)} {im.size} {im.format} {p.stat().st_size}")
        except Exception as e:
            print("ERR",p,e)