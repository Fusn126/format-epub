# format-epub

一些用于处理EPUB电子书的Python脚本。

## 功能

### 主要功能
- **改变图片标签**: 将EPUB中的SVG图片标签转换为IMG标签
- **图片自适应**: 自动调整EPUB文件中图片的大小,使其自适应屏幕
- **完整处理**: 先改变图片标签，再对图片进行自适应处理

## 使用方法

### 方法1: 使用用户界面 (推荐)

1. 安装依赖:

```bash
pip install -r requirements.txt
```

2. 运行用户界面:

```bash
# 默认处理项目根目录的EPUB文件
python setup.py

# 指定目录处理EPUB文件
python setup.py -d /path/to/epub/files
python setup.py --dir "C:\Books\EPUB"
```

3. 按照菜单提示选择功能:
   - 选择 `1`: 改变图片标签 (将SVG转换为IMG)
   - 选择 `2`: 图片自适应 (添加响应式样式)
   - 选择 `3`: 完整处理 (先改变标签，再自适应)
   - 选择 `4`: 查看当前目录的EPUB文件
   - 选择 `5`: 退出

### 方法1.5: 命令行直接执行(无需交互)

```bash
# 改变图片标签
python setup.py -d /path/to/epub/files -a change_tag

# 图片自适应
python setup.py -d /path/to/epub/files -a resize

# 完整处理(先改变标签,再自适应)
python setup.py -d /path/to/epub/files -a all

# 查看帮助信息
python setup.py -h
```

### 方法2: 直接运行脚本

#### epub_change_img_tag.py

```bash
python scripts/epub_change_img_tag.py
```

- 将epub中的svg图片标签转换为img标签
- 移除figure标签，保留图片内容

#### epub_img_resize.py

```bash
python scripts/epub_img_resize.py
```

- 自动调整EPUB文件中图片的大小,使其自适应屏幕
- 移除图片的固定宽高属性
- 添加响应式CSS样式
- 支持批量处理当前目录下的所有EPUB文件

## 项目结构

```
format-epub/
├── setup.py                    # 用户界面主程序
├── scripts/                    # 脚本文件
│   ├── epub_change_img_tag.py  # 改变图片标签脚本
│   └── epub_img_resize.py      # 图片自适应脚本
├── requirements.txt            # 依赖包列表
├── README.md                   # 项目说明
└── .gitignore                  # Git忽略文件
```

## 命令行参数说明

- `-d, --dir`: 指定EPUB文件所在的目录路径(可选,默认为项目根目录)
- `-a, --action`: 直接执行指定操作,跳过交互式菜单
  - `change_tag`: 改变图片标签
  - `resize`: 图片自适应
  - `all`: 完整处理
- `-h, --help`: 显示帮助信息

## 注意事项

1. 默认处理项目根目录中的EPUB文件,也可以通过`-d`参数指定其他目录
2. 脚本会自动处理指定目录下的所有.epub文件
3. 处理过程中会创建临时文件，完成后会自动清理
4. 建议在处理前备份原始EPUB文件

## 依赖包

- beautifulsoup4==4.13.3
- EbookLib==0.18
- html5lib==1.1
- lxml==5.3.1
- six==1.17.0
- soupsieve==2.6
- typing_extensions==4.12.2
- webencodings==0.5.1



