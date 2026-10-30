import pathlib
p=pathlib.Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.md")
lines=p.read_text(encoding="utf-8").splitlines()
out=[]
for line in lines:
    s=line.strip()
    if s=="## 目录":
        out.append("<!-- pagebreak -->")
        out.append("")
        out.append(line)
        continue
    if s.startswith("附录 ") and not s.startswith("附录 A 工程结构") is False:
        pass
    if s.startswith("附录 ") and not s.startswith("附录 A 工程结构"):
        # appendix TOC entries (plain lines, not headings)
        out.append("- "+s)
        continue
    if s.startswith("附录 A") and not s.startswith("##"):
        out.append("- "+s); continue
    if s.startswith("附录 B") and not s.startswith("##"):
        out.append("- "+s); continue
    if s.startswith("附录 C") and not s.startswith("##"):
        out.append("- "+s); continue
    if s.startswith("附录 D") and not s.startswith("##"):
        out.append("- "+s); continue
    out.append(line)
p.write_text("\n".join(out)+"\n",encoding="utf-8")
print("ok")