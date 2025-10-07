#!/usr/bin/env python3
"""
EPUB处理工具 - 用户界面
提供多种EPUB处理功能的统一入口
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    return current_file.parent


def find_epub_files(directory: str = ".") -> List[Path]:
    """查找目录下的所有EPUB文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"错误：目录不存在: {directory}")
        return []
    if not dir_path.is_dir():
        print(f"错误：路径不是目录: {directory}")
        return []
    return list(dir_path.glob("*.epub"))


def run_script(script_name: str, target_dir: Optional[str] = None) -> bool:
    """运行指定的脚本

    Args:
        script_name: 脚本名称
        target_dir: 目标目录路径(可选),如果指定则切换到该目录运行脚本
    """
    try:
        script_path = get_project_root() / "scripts" / script_name
        if not script_path.exists():
            print(f"错误：找不到脚本 {script_name}")
            return False

        print(f"正在运行脚本: {script_name}")
        print("-" * 50)

        # 切换到指定目录或项目根目录运行脚本
        original_cwd = os.getcwd()
        work_dir = target_dir if target_dir else str(get_project_root())
        os.chdir(work_dir)

        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=False, text=True
        )

        os.chdir(original_cwd)
        return result.returncode == 0

    except Exception as e:
        print(f"运行脚本时出错: {str(e)}")
        return False


def process_epub_files(script_name: str, target_dir: Optional[str] = None) -> None:
    """处理EPUB文件

    Args:
        script_name: 脚本名称
        target_dir: 目标目录路径(可选)
    """
    search_dir = target_dir if target_dir else "."
    epub_files = find_epub_files(search_dir)

    if not epub_files:
        print(f"在目录 '{search_dir}' 下没有找到epub文件")
        print("请确保epub文件在指定目录中")
        return

    print(f"找到 {len(epub_files)} 个epub文件:")
    for i, epub_file in enumerate(epub_files, 1):
        print(f"  {i}. {epub_file.name}")

    print(f"\n开始运行 {script_name}...")
    success = run_script(script_name, target_dir)

    if success:
        print(f"\n✅ {script_name} 执行完成")
    else:
        print(f"\n❌ {script_name} 执行失败")


def show_menu() -> None:
    """显示主菜单"""
    print("=" * 60)
    print("           EPUB处理工具")
    print("=" * 60)
    print("请选择要执行的功能:")
    print("1. 改变图片标签 (将SVG转换为IMG)")
    print("2. 图片自适应 (添加响应式样式)")
    print("3. 完整处理 (先改变标签，再自适应)")
    print("4. 查看当前目录的EPUB文件")
    print("5. 退出")
    print("-" * 60)


def get_user_choice() -> Optional[int]:
    """获取用户选择"""
    try:
        choice = input("请输入选择 (1-5): ").strip()
        return int(choice)
    except ValueError:
        print("请输入有效的数字 (1-5)")
        return None


def handle_choice(choice: int, target_dir: Optional[str] = None) -> bool:
    """处理用户选择

    Args:
        choice: 用户选择的功能编号
        target_dir: 目标目录路径(可选)
    """
    if choice == 1:
        print("\n🔄 选择功能: 改变图片标签")
        process_epub_files("epub_change_img_tag.py", target_dir)
        return True

    elif choice == 2:
        print("\n🔄 选择功能: 图片自适应")
        process_epub_files("epub_img_resize.py", target_dir)
        return True

    elif choice == 3:
        print("\n🔄 选择功能: 完整处理")
        print("步骤1: 改变图片标签...")
        if run_script("epub_change_img_tag.py", target_dir):
            print("步骤2: 图片自适应...")
            run_script("epub_img_resize.py", target_dir)
        return True

    elif choice == 4:
        search_dir = target_dir if target_dir else "."
        print(f"\n📁 目录 '{search_dir}' 的EPUB文件:")
        epub_files = find_epub_files(search_dir)
        if epub_files:
            for i, epub_file in enumerate(epub_files, 1):
                print(f"  {i}. {epub_file.name}")
        else:
            print("  没有找到EPUB文件")
        return True

    elif choice == 5:
        print("\n👋 感谢使用EPUB处理工具！")
        return False

    else:
        print("❌ 无效选择，请输入 1-5 之间的数字")
        return True


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="EPUB处理工具 - 提供多种EPUB处理功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互式菜单(默认在项目根目录查找EPUB)
  python setup.py
  
  # 指定目录处理EPUB文件
  python setup.py -d /path/to/epub/files
  python setup.py --dir "C:\\Books\\EPUB"
  
  # 直接运行特定功能
  python setup.py -d /path/to/epub/files -a change_tag
  python setup.py -d /path/to/epub/files -a resize
  python setup.py -d /path/to/epub/files -a all
        """,
    )

    parser.add_argument(
        "-d",
        "--dir",
        dest="target_dir",
        type=str,
        default=None,
        help="指定EPUB文件所在的目录路径(默认为当前项目根目录)",
    )

    parser.add_argument(
        "-a",
        "--action",
        dest="action",
        type=str,
        choices=["change_tag", "resize", "all"],
        default=None,
        help="直接执行指定操作: change_tag(改变图片标签), resize(图片自适应), all(完整处理)",
    )

    return parser.parse_args()


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()

    print("正在启动EPUB处理工具...")

    # 显示工作目录信息
    if args.target_dir:
        target_path = Path(args.target_dir).resolve()
        if not target_path.exists():
            print(f"❌ 错误：指定的目录不存在: {args.target_dir}")
            return
        if not target_path.is_dir():
            print(f"❌ 错误：指定的路径不是目录: {args.target_dir}")
            return
        print(f"📁 工作目录: {target_path}")
    else:
        print(f"📁 工作目录: {get_project_root()} (项目根目录)")

    # 检查依赖
    try:
        import ebooklib
        import bs4

        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return

    # 如果指定了action参数,直接执行对应操作
    if args.action:
        if args.action == "change_tag":
            print("\n🔄 执行功能: 改变图片标签")
            process_epub_files("epub_change_img_tag.py", args.target_dir)
        elif args.action == "resize":
            print("\n🔄 执行功能: 图片自适应")
            process_epub_files("epub_img_resize.py", args.target_dir)
        elif args.action == "all":
            print("\n🔄 执行功能: 完整处理")
            print("步骤1: 改变图片标签...")
            if run_script("epub_change_img_tag.py", args.target_dir):
                print("步骤2: 图片自适应...")
                run_script("epub_img_resize.py", args.target_dir)
        print("\n✅ 操作完成")
        return

    # 交互式菜单模式
    while True:
        show_menu()
        choice = get_user_choice()

        if choice is None:
            continue

        should_continue = handle_choice(choice, args.target_dir)
        if not should_continue:
            break

        # 询问是否继续
        if choice in [1, 2, 3]:
            print("\n" + "=" * 60)
            continue_choice = input("是否继续处理其他文件？(y/n): ").strip().lower()
            if continue_choice not in ["y", "yes", "是"]:
                print("👋 感谢使用EPUB处理工具！")
                break


if __name__ == "__main__":
    main()
