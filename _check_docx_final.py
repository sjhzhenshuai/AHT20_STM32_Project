from docx import Document
p=r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.docx"
d=Document(p)
print("paragraphs",len(d.paragraphs),"tables",len(d.tables),"images",len(d.inline_shapes))
print("date paragraphs",sum(1 for x in d.paragraphs if "2026 年 10 月 30 日" in x.text))
print("headings",sum(1 for x in d.paragraphs if x.style.name.startswith("Heading")))