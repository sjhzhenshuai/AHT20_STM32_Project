from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
root=Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4")
font_path=r"C:\Windows\Fonts\msyh.ttc"
font=ImageFont.truetype(font_path,20)
small=ImageFont.truetype(font_path,16)
for group, folder in [("t1",root/"任务1"/"任务一实验结果截图"),("t2",root/"任务2"/"任务二实验结果截图")]:
    files=[p for p in sorted(folder.iterdir()) if p.suffix.lower() in (".png",".jpg",".jpeg")]
    cols=4; tw,th=480,320; label_h=70; rows=(len(files)+cols-1)//cols
    W=cols*tw; H=rows*(th+label_h)
    sheet=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(sheet)
    for i,p in enumerate(files):
        r,c=divmod(i,cols)
        x=c*tw; y=r*(th+label_h)
        try:
            im=Image.open(p).convert("RGB")
            im.thumbnail((tw-20,th-10))
            ox=x+(tw-im.width)//2; oy=y+(th-im.height)//2
            sheet.paste(im,(ox,oy))
        except Exception as e:
            d.text((x+10,y+10),f"ERR {e}",fill="red",font=small)
        name=p.name
        d.rectangle([x,y+th,x+tw,y+th+label_h],fill="#f4f6f9")
        d.text((x+8,y+th+6),f"{i+1:02d}",fill="#1f3a5f",font=font)
        # wrap name to 46 chars
        line1=name[:46]; line2=name[46:92]
        d.text((x+8,y+th+30),line1,fill="#222",font=small)
        if line2: d.text((x+8,y+th+50),line2,fill="#222",font=small)
    out=Path(r"F:\Keil files\AHT20")/f"_contact_{group}.jpg"
    sheet.save(out,quality=90)
    print(out,len(files))