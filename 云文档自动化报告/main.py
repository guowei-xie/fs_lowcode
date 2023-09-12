from library.fs_doc import *
import subprocess

doc_id = "HdxVdhaBToe0IyxOgiUcHlTynK9"
doc = Doc(document_id=doc_id)

# 生成报告素材
subprocess.call(["Rscript", "Rplot.R"])

# 清空云文档
doc.clean()

# 生成报告内容
## H1标题
doc.h1(content="1.背景")
## 纯文本
doc.text(content="这份报告是为了演示云文档自动化的过程，这份报告当中的所有内容均是自动化生成，借用可视化培训时使用的R画图素材来进行演示，在上次的可视化培训当中我们介绍了以下几种图表：") # 创建纯文本
## 样式文本容器
doc.text_add(content="分别是 ")
doc.text_add(content="方差图", text_element_style={"background_color": 1})
doc.text_add(content="、")
doc.text_add(content="哑铃图、", text_element_style={"background_color": 2})
doc.text_add(content="和")
doc.text_add(content="坡度图。", text_element_style={"background_color": 3})
doc.text_add(content="（这里演示了样式文本块的使用）")
## 推送并重置容器
doc.text_commit()


doc.h1(content="2.可视化")
doc.h2(content="2.1方差图")
doc.text(content="使用方差图来展示不同学期下每个老师的续报率分布。（这里演示了单张图片的自动化上传）")
## 纯图片
doc.img(img_path="img/plot1.jpeg")

doc.h2(content="2.2哑铃图与坡度图")
doc.text(content="使用哑铃图和坡度图来展示各老师在连续两个期次当中的续报率水平是否存在普遍升或降的情况。（这里演示了多张图片的分列摆放）")
## 添加多张图片到容器（最多5张）
doc.img_add(img_path="img/plot2.jpeg")
doc.img_add(img_path="img/plot3.jpeg")
## 推送并重置容器
doc.img_commit()