from docx import Document
p=r"G:\文件\个人文件\作业\嵌入式基础\实验4\实验4_综合实验报告.docx"
d=Document(p)
removed=0
for para in list(d.paragraphs):
    if para.text.strip()=="2026 年 10 月 30 日":
        para._element.getparent().remove(para._element)
        removed+=1
d.save(p)
print("removed",removed)