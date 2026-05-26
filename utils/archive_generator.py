import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from utils.logger import log
from config import SKIP_EMPTY_ZIP

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
        import json

        # 尝试读取上一次生成的压缩包的文件名，即使目录下已经没有该文件，也确保不会生成重名压缩包
        last_filenamejson = Path(self.archives_dir) / 'last_archive_name.json'
        if os.path.exists(str(last_filenamejson)):
            with open(last_filenamejson, 'r', encoding='utf-8') as f:
                last_filename = json.load(f)  # 读取上次成功生成压缩包的文件名
        else:
            last_filename = None

        sn = 1  # 压缩包序号
        while True:  # 找到一个不重名的压缩包名称，避免一天多次运行而覆盖上一个压缩包
            filename = "packages_{}{}.zip".format(
                today_str, ('' if sn == 1 else '_' + str(sn))
                )
            if last_filename is not None and last_filename > filename:
                filename = last_filename
            archive_path = Path(self.archives_dir) / filename
            if os.path.exists(str(archive_path)) or filename == last_filename:
                sn += 1
            else:
                break
        # print(archive_path)
        # 20251125修改为先生成需压缩文件的列表，再根据是否不生成空压缩包的配置来工作
        filelist = []
        for root, dirs, files in os.walk(self.packages_dir):
            for file in files:
                print(root, file)
                file_path = Path(root) / file
                filelist.append((file_path, file_path.name))
        if SKIP_EMPTY_ZIP and len(files) == 0:
            log.info(f"本次未发现新的包文件，按配置【SKIP_EMPTY_ZIP】要求不生成压缩包")
        else:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历 data 文件夹中的所有文件和子文件夹
                for file_path, file_name in filelist:
                    # zipf.write(file_path, file_name)
                    zipf.write(file_path, filename[:-4] + '/' + file_name)
                    log.debug(f"已添加: {file_name}")
            log.info(f"压缩完成: {filename}")
            log.info(f"压缩文件大小: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")
            # 保存刚刚生成的压缩包的文件名
            with open(last_filenamejson, 'w', encoding='utf-8') as f:
                json.dump(filename, f)

        return True


def main():
    import shutil

    archive = ArchiveGenerator()
    archive.create_daily_archive()

    # 20251121增加归档后删除下载文件
    folder_path = "data/packages"
    # 先删除整个目录
    shutil.rmtree(folder_path)
    # 然后重新创建空目录
    os.makedirs(folder_path)
    
    log.info(f"成功清空目录: {folder_path}")


