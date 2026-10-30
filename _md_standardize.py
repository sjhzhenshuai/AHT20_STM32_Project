import re, pathlib
p=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md")
lines=p.read_text(encoding="utf-8").splitlines()
out=[]
for line in lines:
    m=re.match(r"^!img\s+(\S+)\s*\|\s*(.+)$",line.strip())
    if m:
        path,cap=m.group(1),m.group(2).strip()
        out.append(f"![{cap}]({path})")
        out.append("")
        out.append(f"*{cap}*")
        continue
    m=re.match(r"^!video\s+(\S+)\s*\|\s*(.+)$",line.strip())
    if m:
        path,cap=m.group(1),m.group(2).strip()
        out.append(f"[{cap}]({path})")
        out.append("")
        out.append(f"*{cap}*")
        continue
    if line.strip()=="!pagebreak":
        out.append("<!-- pagebreak -->")
        continue
    out.append(line)
p.write_text("\n".join(out)+"\n",encoding="utf-8")
print("lines",len(out))