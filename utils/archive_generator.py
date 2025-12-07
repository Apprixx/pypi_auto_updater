import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from utils.logger import log


class ArchiveGenerator:
    """
    压缩文件生成器：
    - 收集每日下载文件
    - 生成按日期命名的压缩包
    - 验证压缩文件完整性
    - 清理旧归档
    """

    def __init__(self, packages_dir: Optional[Path] = "data/packages", archives_dir: Optional[Path] = "data/archives"):
        self.packages_dir = packages_dir 
        self.archives_dir = archives_dir 


    # 创建每日压缩包
    def create_daily_archive(self) -> Optional[Path]:
        today_str = datetime.now().strftime("%Y-%m-%d")
        archive_name = f"packages_{today_str}.zip"
        archive_path = Path(self.archives_dir) / archive_name
        # try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历 data 文件夹中的所有文件和子文件夹
            for root, dirs, files in os.walk(self.packages_dir):
                for file in files:
                    file_path = Path(root) / file
                    # 计算在 zip 文件中的相对路径
                    arcname = file_path.relative_to(self.packages_dir)
                    zipf.write(file_path, arcname)
                    log.debug(f"已添加: {arcname}")
        
        log.info(f"压缩完成: {self.archives_dir}")
        log.info(f"压缩文件大小: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")
        return True


def main():
    archive = ArchiveGenerator()
    archive.create_daily_archive()
