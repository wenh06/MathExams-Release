# 数学考试试题及答案库

## 说明

本仓库基于 [exam-zh](https://ctan.org/pkg/exam-zh)，包含中国农业大学多门数学课程的考试试题及答案，包括

- [实变函数](content/实变函数/)
- [数学分析](content/数学分析/)
- [微积分I（高等数学C）](content/微积分/)

## 编译

本仓库使用 `xelatex` 编译，编译命令为（需要两次编译, 以生成正确的页脚中的总页数）：

```bash
xelatex main.tex && xelatex main.tex
```

或者使用 [`compile.py`](compile.py) 脚本（生成的文件在 [`build`](build) 目录下）：

```bash
python compile.py
```

## Linux (Ubuntu) 系统下字体缺失问题

Linux (Ubuntu) 系统下编译可能遇到例如 `Arial` 等字体缺失问题，需要执行如下命令安装：

```bash
sudo apt install ttf-mscorefonts-installer
sudo fc-cache -f
```
