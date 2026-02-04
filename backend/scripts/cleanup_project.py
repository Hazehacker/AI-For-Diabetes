#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本 - 【工具脚本】
~~~~~~~~~~~~~~~

清理项目中标记为可删除的文件和目录

执行前请务必备份重要数据！

清理内容：
- __pycache__ 目录（Python字节码缓存）
- 日志文件目录 (logs/)
- TTS缓存目录 (tts_cache/)
- 临时测试文件 (*.DELETE标记的文件)
- 临时修复文档 (*.DELETE标记的文件)

作者: 智糖团队
日期: 2025-01-21
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 要清理的文件和目录
CLEANUP_ITEMS = [
    # 目录
    ("__pycache__", "Python字节码缓存目录"),
    ("logs", "运行时日志文件目录"),
    ("tts_cache", "TTS语音缓存目录"),

    # 文件模式 (文件名模式, 描述)
    ("*.pyc", "Python编译文件"),
    ("*.DELETE", "标记为删除的文件"),
]

def find_cleanup_files() -> List[Tuple[Path, str]]:
    """
    查找需要清理的文件和目录

    Returns:
        List[Tuple[Path, str]]: (文件路径, 描述) 的列表
    """
    cleanup_files = []

    # 遍历所有清理项目
    for item in CLEANUP_ITEMS:
        if len(item) == 2:
            # 目录
            dir_name, description = item
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists() and dir_path.is_dir():
                cleanup_files.append((dir_path, f"{description} ({dir_name}/)"))
        else:
            # 文件模式
            pattern, description = item
            for file_path in PROJECT_ROOT.glob(f"**/{pattern}"):
                if file_path.is_file():
                    cleanup_files.append((file_path, f"{description} ({file_path.name})"))

    return cleanup_files

def calculate_size(files: List[Tuple[Path, str]]) -> str:
    """计算文件总大小"""
    total_size = 0
    for file_path, _ in files:
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass
        elif file_path.is_dir():
            try:
                for root, dirs, files_in_dir in os.walk(file_path):
                    for file in files_in_dir:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass
            except OSError:
                pass

    # 格式化大小
    if total_size < 1024:
        return f"{total_size} bytes"
    elif total_size < 1024 * 1024:
        return f"{total_size / 1024:.1f} KB"
    elif total_size < 1024 * 1024 * 1024:
        return f"{total_size / (1024 * 1024):.1f} MB"
    else:
        return f"{total_size / (1024 * 1024 * 1024):.1f} GB"

def main():
    """主函数"""

    # 查找需要清理的文件
    cleanup_files = find_cleanup_files()

    if not cleanup_files:
        return

    # 分类显示
    dirs_to_cleanup = []
    files_to_cleanup = []

    for file_path, description in cleanup_files:
        if file_path.is_dir():
            dirs_to_cleanup.append((file_path, description))
        else:
            files_to_cleanup.append((file_path, description))




    # 显示统计信息
    total_size = calculate_size(cleanup_files)


    # 确认清理
    while True:
        response = input("❓ 确认要删除这些文件吗？(yes/no): ").strip().lower()
        if response in ['yes', 'y', '是']:
            break
        elif response in ['no', 'n', '否']:
            return


    deleted_count = 0
    error_count = 0

    # 执行清理
    for file_path, description in cleanup_files:
        try:
            deleted_count += 1
        except Exception as e:
            error_count += 1



if __name__ == '__main__':
    main()
