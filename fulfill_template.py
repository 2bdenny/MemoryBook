# -*- coding: utf-8 -*-
import imagesize
import re
import sys
import os.path
from os import listdir, walk
from os.path import join, basename, isfile

template_vertical_pic = """
\setlength{\columnsep}{1cm}
\\begin{multicols}{2}
\\begin{figure}[H]
    \centering
     \includegraphics[width=0.5\\textwidth,height=1\\textheight,keepaspectratio]{%s}
\end{figure}
\section{%s}
\\begin{parchment}[毕业赠言]
%s
\end{parchment}
\\begin{parchment}[联系方式]
  \\begin{itemize}
  %s
  \end{itemize}
\end{parchment}
\end{multicols}
\FloatBarrier
%\\newpage
"""

template_horizontal_pic = """
\setlength{\columnsep}{1cm}
\\begin{multicols}{2}
\\begin{figure}[H]
    \centering
     \includegraphics[width=0.5\\textwidth,height=1\\textheight,keepaspectratio]{%s}
\end{figure}
\section{%s}
\\vfill\\null
\columnbreak
\\begin{parchment}[毕业赠言]
%s
\end{parchment}
\\begin{parchment}[联系方式]
  \\begin{itemize}
  %s
  \end{itemize}
\end{parchment}
\end{multicols}
\FloatBarrier
\\newpage
"""

def readFile(fileDir):
    content = ''
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
    for e in encodings:
        try:
            with open(fileDir, 'r', encoding = e) as f:
                content = f.read()
        except UnicodeDecodeError:
            # print('Error code %s' % e
            continue
        else:
            # print('True code %s' % e)
            break
    return content

def getStudentsInClass(cls):
    print('Class ', cls)

    students = []
    clsDir = 'static/Class' + str(cls)
    # 对于班级里的所有人
    for dir in listdir(clsDir):
        personDir = join(clsDir, dir)
        things = listdir(personDir)

        find_note = False       # 先找留言
        find_contact = False    # 然后找联系方式
        find_pic = False

        # 提取姓名
        name = ''
        if re.search('_', dir):
            name = dir.split('_')[1]
        elif re.search('-', dir):
            name = dir.split('-')[1]
        else:
            print(dir)
            return

        # 提取留言和联系方式
        note_content = ''
        contact_content = ''
        pics = []
        for thing in things:
            thingDir = join(personDir,thing)
            if isfile(thingDir):
                # 识别留言文件
                if re.search('言', thing) or re.search('语', thing) or re.search('message', thing) or re.search('祝福', thing):
                    # 读取留言
                    note_content = readFile(thingDir)
                    if (len(note_content) > 0):
                        find_note = True

                # 识别联系方式文件
                if re.search('联系', thing) or re.search('contact', thing):
                    # 读取联系方式
                    contact_content = readFile(thingDir)
                    if (len(contact_content) > 0):
                        find_contact = True

        # 提取照片
        for (dir, dirnames, files) in walk(personDir):
            # 识别照片
            for f in files:
                if re.search('(jpe?g)|(png)|(JPE?G)|(PNG)$', f):
                    pics.append(join(dir, f))
                    find_pic = True

        if len(pics) == 0:
            pics.append('static/default.png')
        if len(note_content) == 0:
            note_content = '404 NOT FOUND'
            # note_content = '\lipsum[5]'
        if len(contact_content) == 0:
            contact_content = '404 NOT FOUND'

        note_content = re.sub('_', '\_', note_content)
        contact_content = re.sub('_', '\_', contact_content)

        note_content = re.sub('&', '\&', note_content)
        contact_content = re.sub('&', '\&', contact_content)
        # if find_note:
        #     print(personDir + ' Note OK')
        # else:
        #     print(personDir + ' Note not found')
        #
        # if find_contact:
        #     print(personDir + ' Contact OK')
        # else:
        #     print(personDir + ' Contact not found')
        #
        # if find_pic:
        #     print(personDir, ' Pic: ', pics)
        # else:
        #     print(personDir, ' Pic not found')

        one_student = (name, pics, note_content, contact_content)
        students.append(one_student)
    return students

def genTemplate(one_student):
    contact_text = ''
    contact_lines = one_student[3].split('\n')
    for line in contact_lines:
        if len(line) == 0 or re.match('^\s+$', line):
            continue
        contact_text += '\item ' + line + '\n'

    pic = one_student[1][0]
    pic_width, pic_height = imagesize.get(pic)
    text = ''
    if pic_width / pic_height < 1.3:
        # text = template_vertical_pic % (one_student[1][0], one_student[0], one_student[2], contact_text)
        text = template_vertical_pic % (one_student[1][0], '测试姓名', one_student[2], '\item 测试文字测试文字')
    else:
        # text = template_horizontal_pic % (one_student[1][0], one_student[0], one_student[2], contact_text)
        text = template_horizontal_pic % (one_student[1][0], '测试姓名', one_student[2], '\item 测试文字测试文字')
    return text


tex_head = ''
with open('template.tex', 'r') as temp:
    tex_head = temp.read()
tex_tail = """

\end{document}
"""

with open('main.tex', 'w') as m:
    m.write(tex_head)
    for i in range(1, 5):
        students = getStudentsInClass(i)
        for student in students:
            text = genTemplate(student)
            m.write(text)
            m.write('\n')
            # break
    m.write(tex_tail)
