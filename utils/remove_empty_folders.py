import os
from utils.logger import log

def remove_empty_folders_simple(folder_path: str = "data/packages") -> int:
    """
    最简单的空文件夹删除函数
    返回删除的文件夹数量
    """
    count = 0
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # 跳过根目录，只处理子目录
        if root != folder_path and not dirs and not files:
            try:
                os.rmdir(root)
                count += 1
                log.debug(f"删除: {root}")
            except OSError:
                pass  # 删除失败
    log.info(f"共删除了 {count} 个空文件夹")
    return count
