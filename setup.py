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
from typing import List, Optional, Tuple
from enum import Enum


# ==================== 常量定义 ====================
class Action(Enum):
    """操作类型枚举"""

    CHANGE_TAG = (
        "change_tag",
        "epub_change_img_tag.py",
        "改变图片标签 (将SVG转换为IMG)",
    )
    RESIZE = ("resize", "epub_img_resize.py", "图片自适应 (添加响应式样式)")
    ALL = ("all", None, "完整处理 (先改变标签，再自适应)")

    def __init__(self, action_name: str, script_name: Optional[str], description: str):
        self.action_name = action_name
        self.script_name = script_name
        self.description = description


# 菜单选项映射
MENU_ACTIONS = {
    1: Action.CHANGE_TAG,
    2: Action.RESIZE,
    3: Action.ALL,
    4: "list_files",
    5: "exit",
}


# ==================== 工具函数 ====================
def print_header(title: str, char: str = "=", width: int = 60) -> None:
    """打印格式化的标题"""
    print(char * width)
    print(f"{title:^{width}}")
    print(char * width)


def print_section(title: str, char: str = "-", width: int = 60) -> None:
    """打印分节标题"""
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def print_success(message: str) -> None:
    """打印成功消息"""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """打印错误消息"""
    print(f"❌ {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """打印信息消息"""
    print(f"ℹ️  {message}")


def print_warning(message: str) -> None:
    """打印警告消息"""
    print(f"⚠️  {message}")


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent


# ==================== 核心功能 ====================
def find_epub_files(directory: str = ".") -> List[Path]:
    """查找目录下的所有EPUB文件

    Args:
        directory: 要搜索的目录路径

    Returns:
        EPUB文件路径列表
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists():
        print_error(f"目录不存在: {directory}")
        return []

    if not dir_path.is_dir():
        print_error(f"路径不是目录: {directory}")
        return []

    epub_files = sorted(dir_path.glob("*.epub"))
    return epub_files


def validate_directory(directory: Optional[str]) -> Tuple[bool, Optional[Path]]:
    """验证目录是否有效

    Args:
        directory: 目录路径

    Returns:
        (是否有效, 解析后的路径)
    """
    if directory is None:
        return True, None

    target_path = Path(directory).resolve()

    if not target_path.exists():
        print_error(f"指定的目录不存在: {directory}")
        return False, None

    if not target_path.is_dir():
        print_error(f"指定的路径不是目录: {directory}")
        return False, None

    return True, target_path


def run_script(script_name: str, target_dir: Optional[str] = None) -> bool:
    """运行指定的脚本

    Args:
        script_name: 脚本名称
        target_dir: 目标目录路径(可选)

    Returns:
        脚本是否成功执行
    """
    script_path = get_project_root() / "scripts" / script_name

    if not script_path.exists():
        print_error(f"找不到脚本: {script_name}")
        return False

    print_info(f"正在运行脚本: {script_name}")
    print_section("", "-", 50)

    # 保存当前目录
    original_cwd = os.getcwd()

    try:
        # 切换到指定目录或项目根目录
        work_dir = target_dir if target_dir else str(get_project_root())
        os.chdir(work_dir)

        # 运行脚本
        result = subprocess.run(
            [sys.executable, str(script_path)], capture_output=False, text=True
        )

        return result.returncode == 0

    except subprocess.SubprocessError as e:
        print_error(f"运行脚本时出错: {str(e)}")
        return False

    except Exception as e:
        print_error(f"未预期的错误: {str(e)}")
        return False

    finally:
        # 恢复原目录
        os.chdir(original_cwd)


def process_epub_files(action: Action, target_dir: Optional[str] = None) -> bool:
    """处理EPUB文件

    Args:
        action: 要执行的操作
        target_dir: 目标目录路径(可选)

    Returns:
        处理是否成功
    """
    search_dir = target_dir if target_dir else "."
    epub_files = find_epub_files(search_dir)

    if not epub_files:
        print_warning(f"在目录 '{Path(search_dir).resolve()}' 下没有找到EPUB文件")
        print_info("请确保EPUB文件在指定目录中")
        return False

    print_info(f"找到 {len(epub_files)} 个EPUB文件:")
    for i, epub_file in enumerate(epub_files, 1):
        print(f"  {i}. {epub_file.name}")

    print("\n开始处理...")

    # 处理单个脚本
    if action.script_name:
        success = run_script(action.script_name, target_dir)
        if success:
            print_success(f"{action.description} 执行完成")
        else:
            print_error(f"{action.description} 执行失败")
        return success

    # 处理组合操作（ALL）
    elif action == Action.ALL:
        print_section("步骤 1/2: 改变图片标签", "-", 50)
        if run_script(Action.CHANGE_TAG.script_name, target_dir):
            print_success("步骤 1 完成")
            print_section("步骤 2/2: 图片自适应", "-", 50)
            if run_script(Action.RESIZE.script_name, target_dir):
                print_success("步骤 2 完成")
                return True
            else:
                print_error("步骤 2 失败")
                return False
        else:
            print_error("步骤 1 失败，跳过步骤 2")
            return False

    return False


def list_epub_files(target_dir: Optional[str] = None) -> None:
    """列出目录中的EPUB文件"""
    search_dir = target_dir if target_dir else "."
    dir_path = Path(search_dir).resolve()

    print_section(f"📁 目录: {dir_path}", "-", 60)

    epub_files = find_epub_files(search_dir)

    if epub_files:
        print(f"找到 {len(epub_files)} 个EPUB文件:\n")
        for i, epub_file in enumerate(epub_files, 1):
            file_size = epub_file.stat().st_size / 1024 / 1024  # MB
            print(f"  {i}. {epub_file.name} ({file_size:.2f} MB)")
    else:
        print_warning("没有找到EPUB文件")


# ==================== 菜单交互 ====================
def show_menu() -> None:
    """显示主菜单"""
    print_header("EPUB处理工具", "=", 60)
    print("请选择要执行的功能:")
    print(f"1. {Action.CHANGE_TAG.description}")
    print(f"2. {Action.RESIZE.description}")
    print(f"3. {Action.ALL.description}")
    print("4. 查看当前目录的EPUB文件")
    print("5. 退出")
    print("-" * 60)


def get_user_choice() -> Optional[int]:
    """获取用户选择

    Returns:
        用户选择的数字，如果输入无效则返回None
    """
    try:
        choice = input("请输入选择 (1-5): ").strip()
        num = int(choice)
        if 1 <= num <= 5:
            return num
        else:
            print_error("请输入 1-5 之间的数字")
            return None
    except ValueError:
        print_error("请输入有效的数字")
        return None
    except KeyboardInterrupt:
        print("\n")
        print_info("用户取消操作")
        return 5  # 退出


def handle_choice(choice: int, target_dir: Optional[str] = None) -> bool:
    """处理用户选择

    Args:
        choice: 用户选择的功能编号
        target_dir: 目标目录路径(可选)

    Returns:
        是否继续运行程序
    """
    action = MENU_ACTIONS.get(choice)

    if action == "exit":
        print("\n👋 感谢使用EPUB处理工具！")
        return False

    elif action == "list_files":
        list_epub_files(target_dir)
        return True

    elif isinstance(action, Action):
        print(f"\n🔄 选择功能: {action.description}")
        process_epub_files(action, target_dir)
        return True

    else:
        print_error("无效选择")
        return True


def ask_continue() -> bool:
    """询问用户是否继续"""
    try:
        print("\n" + "=" * 60)
        response = input("是否继续处理其他文件？(y/n): ").strip().lower()
        return response in ["y", "yes", "是"]
    except KeyboardInterrupt:
        print("\n")
        return False


# ==================== 依赖检查 ====================
def check_dependencies() -> bool:
    """检查必要的依赖是否安装

    Returns:
        依赖是否满足
    """
    required_packages = {
        "ebooklib": "EbookLib",
        "bs4": "beautifulsoup4",
        "lxml": "lxml",
    }

    missing_packages = []

    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print_error("缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print_info("请运行: pip install -r requirements.txt")
        return False

    print_success("依赖检查通过")
    return True


# ==================== 命令行参数 ====================
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
  
  # 静默模式（跳过确认）
  python setup.py -d /path/to/epub/files -a all --quiet
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
        choices=[a.action_name for a in Action],
        default=None,
        help="直接执行指定操作: change_tag(改变图片标签), resize(图片自适应), all(完整处理)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="静默模式，执行完成后直接退出",
    )

    return parser.parse_args()


# ==================== 主函数 ====================
def execute_action_by_name(action_name: str, target_dir: Optional[str]) -> bool:
    """根据操作名称执行对应操作

    Args:
        action_name: 操作名称
        target_dir: 目标目录

    Returns:
        操作是否成功
    """
    for action in Action:
        if action.action_name == action_name:
            print(f"\n🔄 执行功能: {action.description}")
            return process_epub_files(action, target_dir)

    print_error(f"未知操作: {action_name}")
    return False


def main() -> None:
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()

    print_info("正在启动EPUB处理工具...")

    # 验证目标目录
    is_valid, target_path = validate_directory(args.target_dir)
    if not is_valid:
        sys.exit(1)

    # 显示工作目录信息
    if target_path:
        print(f"📁 工作目录: {target_path}")
    else:
        print(f"📁 工作目录: {get_project_root()} (项目根目录)")

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    print()  # 空行分隔

    # 命令行模式：直接执行指定操作
    if args.action:
        success = execute_action_by_name(args.action, args.target_dir)

        if success:
            print_success("操作完成")
            sys.exit(0)
        else:
            print_error("操作失败")
            sys.exit(1)

    # 交互式菜单模式
    try:
        while True:
            show_menu()
            choice = get_user_choice()

            if choice is None:
                continue

            should_continue = handle_choice(choice, args.target_dir)

            if not should_continue:
                break

            # 询问是否继续（仅在处理操作后）
            if choice in [1, 2, 3]:
                if not ask_continue():
                    print("👋 感谢使用EPUB处理工具！")
                    break

    except KeyboardInterrupt:
        print("\n")
        print_info("用户中断程序")
        print("👋 感谢使用EPUB处理工具！")
        sys.exit(0)


if __name__ == "__main__":
    main()
