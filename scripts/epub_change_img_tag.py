from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import warnings
import zipfile
from bs4.builder import XMLParsedAsHTMLWarning

# 忽略BeautifulSoup解析XML时的警告
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def convert_svg_to_img(epub_path: str) -> None:
    """将epub中的svg图片标签转换为img标签"""
    try:
        book = epub.read_epub(epub_path)
        print(f"\n正在处理: {epub_path}")
        print("-" * 50)

        # 遍历所有HTML文件
        for item in book.get_items():
            if isinstance(item, epub.EpubHtml):
                soup = BeautifulSoup(item.content, "lxml")

                # 查找所有figure标签中的svg
                figures = soup.find_all("figure", class_="illust")
                for figure in figures:
                    svg = figure.find("svg")
                    if svg:
                        # 获取image标签的href属性
                        image = svg.find("image")
                        if image and image.get("xlink:href"):
                            img_src = image["xlink:href"]
                            # 创建新的img标签
                            new_img = soup.new_tag("img")
                            new_img["src"] = img_src  # 保持原路径不变
                            # 替换原figure标签
                            figure.replace_with(new_img)

                # 更新内容
                item.content = str(soup).encode("utf-8")

        # 保存修改后的epub
        write_epub(book, epub_path)
        print(f"处理完成: {epub_path}")

    except Exception as e:
        print(f"处理 {epub_path} 时出错: {str(e)}")


def write_epub(book: epub.EpubBook, epub_path: str) -> None:
    """将修改后的内容写入新的epub文件"""
    output_name = epub_path + ".temp"
    input_archive = zipfile.ZipFile(epub_path, "r")
    output_archive = zipfile.ZipFile(output_name, "w")
    file_list = input_archive.infolist()

    for x in range(0, len(file_list)):
        item = input_archive.open(file_list[x])
        content = item.read()

        if file_list[x].filename.endswith(".xhtml"):
            for item in book.get_items():
                if item.file_name in file_list[x].filename:
                    output_archive.writestr(file_list[x].filename, item.content)
        else:
            output_archive.writestr(file_list[x].filename, content)

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
            convert_svg_to_img(epub_name)
        except Exception as e:
            print(f"处理 {epub_name} 时出错: {str(e)}")
            continue

        os.remove(epub_name)
        os.rename(output_name, epub_name)


if __name__ == "__main__":
    main()
