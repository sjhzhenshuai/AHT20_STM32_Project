from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H=1800,1000
img=Image.new("RGB",(W,H),"white")
d=ImageDraw.Draw(img)
f_title=ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc",38)
f_sub=ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc",22)
f_lab=ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc",20)
f_bit=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf",20)
blue=(31,95,168); orange=(197,90,17); dark=(35,45,60); gray=(110,120,130); grid=(225,230,236)
d.text((70,40),"软件 I2C 时序（SCL=PB6，SDA=PB7，7 位地址 0x38，写方向）",font=f_title,fill=dark)
d.text((70,95),"每个半周期 delay_us(2)，SCL 约 100–250 kHz；地址字节 0x70，读方向 0x71",font=f_sub,fill=gray)

x0,x1=180,1700
y_scl_h,y_scl_l=260,350
y_sda_h,y_sda_l=500,590

def line(x1,y1,x2,y2,color=dark,w=3):
    d.line([(x1,y1),(x2,y2)],fill=color,width=w)
def scl(segments):
    for (a,b,level) in segments:
        y=y_scl_h if level else y_scl_l
        line(a,y,b,y,blue)
        # vertical transitions handled by adjacent segments
def sda(segments):
    for (a,b,level) in segments:
        y=y_sda_h if level else y_sda_l
        line(a,y,b,y,orange)

# Build SCL/SDA segments for START + address + ACK + data + ACK + STOP
scl_seg=[(x0,300,1),(300,340,1),(340,380,0)]
sda_seg=[(x0,300,1)]

def add_bit(x,bit,width=60):
    # SCL low half, high half; SDA level set for whole bit
    scl_seg.append((x,x+width/2,0))
    scl_seg.append((x+width/2,x+width,1))
    sda_seg.append((x,x+width,bit))

x=380
addr=[0,1,1,1,0,0,0,0]
for b in addr:
    add_bit(x,b); x+=60
# ACK address
scl_seg.append((x,x+30,0)); scl_seg.append((x+30,x+60,1))
sda_seg.append((x,x+60,0)); x+=60
addr_end=x
# Data 0xBE
data=[1,0,1,1,1,1,1,0]
for b in data:
    add_bit(x,b); x+=60
# ACK data
scl_seg.append((x,x+30,0)); scl_seg.append((x+30,x+60,1))
sda_seg.append((x,x+60,0)); data_end=x+60; x+=60
# STOP: SCL low -> high, SDA low -> high
scl_seg.append((x,x+40,0)); scl_seg.append((x+40,x+100,1))
sda_seg.append((x,x+70,0)); sda_seg.append((x+70,x+100,1))

scl(scl_seg); sda(sda_seg)

# vertical transitions
for i in range(1,len(scl_seg)):
    a,b,l=scl_seg[i-1]; c,d2,l2=scl_seg[i]
    if l!=l2 and b==c:
        line(b,y_scl_h if l else y_scl_l,b,y_scl_l if l else y_scl_h,blue,3)
for i in range(1,len(sda_seg)):
    a,b,l=sda_seg[i-1]; c,d2,l2=sda_seg[i]
    if l!=l2 and b==c:
        line(b,y_sda_h if l else y_sda_l,b,y_sda_l if l else y_sda_h,orange,3)

# bit dashed guides and value labels
for i,b in enumerate(addr):
    xx=380+i*60
    d.line([(xx,180),(xx,650)],fill=grid,width=1)
    d.text((xx+18,395),str(b),font=f_bit,fill=dark)
for i,b in enumerate(data):
    xx=380+9*60+i*60
    d.line([(xx,180),(xx,650)],fill=grid,width=1)
    d.text((xx+18,395),str(b),font=f_bit,fill=dark)

# annotations
def ann(x,text,color=dark,dy=0):
    w=d.textlength(text,font=f_lab)
    d.rectangle([x-w/2-8,690+dy,x+w/2+8,724+dy],fill=(245,248,252),outline=(210,218,228))
    d.text((x-w/2,694+dy),text,font=f_lab,fill=color)
ann(320,"START",dark)
ann(660,"地址 0x70（写） + ACK",dark)
ann(1180,"数据 0xBE + ACK",dark)
ann(1600,"STOP",dark)

# bus labels
d.text((80,275),"SCL",font=f_lab,fill=blue)
d.text((80,515),"SDA",font=f_lab,fill=orange)
# axis line
line(x0,650,x1,650,gray,2)
d.text((x0,660),"时间 →",font=f_lab,fill=gray)

# note
d.text((70,820),"协议要点：START = SCL 高时 SDA 下降；STOP = SCL 高时 SDA 上升；",font=f_sub,fill=dark)
d.text((70,855),"第 9 个 SCL 周期释放 SDA，从机拉低为 ACK；AHT20 地址 0x38，写 0x70 / 读 0x71。",font=f_sub,fill=dark)
d.text((70,890),"本图为根据软件 I2C 代码重建的时序示意，用于对照示波器/逻辑分析仪波形。",font=f_sub,fill=gray)

out=Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\media")
out.mkdir(parents=True,exist_ok=True)
img.save(out/"18.png")
print(out/"18.png")