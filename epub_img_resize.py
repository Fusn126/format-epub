import re
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
import random
import string
import zipfile
import os
import warnings
from bs4.builder import XMLParsedAsHTMLWarning

# 忽略BeautifulSoup解析XML时的警告
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 临时epub文件名
TEMP_EPUB_FILE = f"_temp_epub_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}.epub"


def write_epub_style(epub_path: str) -> None:
    """为epub文件中的图片添加自适应样式"""
    try:
        book = epub.read_epub(epub_path)
        print(f"\n正在读取: {epub_path}")
        print("-" * 50)

        # 生成随机类名
        fit_class = f"fit-{''.join(random.choices(string.ascii_lowercase, k=4))}"

        # 响应式图片样式
        new_style = f""".{fit_class} {{\n width: auto;\n height: auto;\n max-width: 100%;\n max-height: 100%;\n}}"""

        # 查找style.css文件
        style_item = next(
            (
                item
                for item in book.get_items()
                if re.search(r"/style\.css$", item.file_name)
            ),
            None,
        )

        if style_item:
            style_content = style_item.content.decode()
            style_item.content = style_content + "\n" + new_style
            print(f"在现有CSS中添加样式: {style_item.file_name}")
        else:
            print("未找到style.css，创建新的CSS文件。")
            style_item = epub.EpubItem(
                uid="style",
                file_name="Styles/style.css",
                media_type="text/css",
                content=new_style,
            )
            book.add_item(style_item)
            for item in book.get_items():
                if isinstance(item, epub.EpubHtml):
                    soup = BeautifulSoup(item.content, "lxml")
                    link = soup.new_tag(
                        "link",
                        href="../Styles/style.css",
                        rel="stylesheet",
                        type="text/css",
                    )
                    soup.head.append(link)
                    item.content = str(soup).encode("utf-8")

    except Exception as e:
        print(f"处理 {epub_path} 时出错: {str(e)}")
        return

    change_epub_html(book, epub_path, fit_class)


def change_epub_html(book: epub.EpubBook, epub_path: str, style_class: str) -> None:
    """修改epub中的图片标签,应用响应式样式"""
    try:
        for item in book.get_items():
            if isinstance(item, epub.EpubHtml):
                modified = False
                soup = BeautifulSoup(item.content, "lxml")

                for img in soup.find_all("img"):
                    # 移除固定尺寸属性
                    for attr in ("width", "height"):
                        if img.has_attr(attr):
                            del img[attr]
                            modified = True

                    # 添加自适应样式类
                    img_classes = img.get("class", [])
                    if isinstance(img_classes, str):
                        img_classes = [img_classes]
                        modified = True
                    if style_class not in img_classes:
                        img_classes.append(style_class)
                        img["class"] = img_classes
                        modified = True

                if modified:
                    item.content = str(soup).encode("utf-8")

    except Exception as e:
        print(f"处理 {epub_path} HTML时出错: {str(e)}")
        return e

    write_epub(book, epub_path)


def write_epub(book: epub.EpubBook, epub_path: str) -> None:
    """将修改后的内容写入新的epub文件"""
    output_name = epub_path + ".temp"
    input_archive = zipfile.ZipFile(epub_path, "r")
    output_archive = zipfile.ZipFile(output_name, "w")
    file_list = input_archive.infolist()

    for x in range(0, len(file_list)):
        item = input_archive.open(file_list[x])
        content = item.read()
        modified = False

        if file_list[x].filename.endswith(".xhtml") or file_list[x].filename.endswith(
            ".css"
        ):
            for item in book.get_items():
                if item.file_name in file_list[x].filename:
                    output_archive.writestr(file_list[x].filename, item.content)
                    if item.file_name == "Styles/style.css":
                        modified = True
        else:
            output_archive.writestr(file_list[x].filename, content)

    if not modified:
        # 写入style.css和content.opf
        for item in book.get_items():
            if item.file_name == "Styles/style.css":
                output_archive.writestr("OEBPS/Styles/style.css", item.content)
        epub.write_epub(TEMP_EPUB_FILE, book)
        opf_message_input_archive = zipfile.ZipFile(TEMP_EPUB_FILE, "r")
        file_list = opf_message_input_archive.infolist()
        for x in range(0, len(file_list)):
            item = opf_message_input_archive.open(file_list[x])
            content = item.read()
            if file_list[x].filename.endswith(".opf"):
                output_archive.writestr("OEBPS/content.opf", content)
        opf_message_input_archive.close()

    input_archive.close()
    output_archive.close()


def main() -> None:
    """处理当前目录下的所有epub文件"""
    epub_files = list(Path(".").glob("*.epub"))

    if not epub_files:
        print("当前目录下没有找到epub文件")
        return

    total = len(epub_files)
    print(f"找到 {total} 个epub文件")

    for i, epub_file in enumerate(epub_files, 1):
        print(f"\n处理进度: {i}/{total}")
        try:
            epub_name = str(epub_file)
            output_name = epub_name + ".temp"
            write_epub_style(epub_name)
        except Exception as e:
            print(f"处理 {epub_name} 时出错: {str(e)}")
            continue

        os.remove(epub_name)
        os.remove(TEMP_EPUB_FILE)
        os.rename(output_name, epub_name)


if __name__ == "__main__":
    main()
