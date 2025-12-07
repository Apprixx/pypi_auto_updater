import os
import json
import requests
import threading
import time
import shutil
import hashlib
from tqdm import tqdm
from typing import Dict
from utils.logger import log
from config import PACKAGE_DOWNLOAD_THREADS

PACKAGES_JSON_PATH = "data/packages.json"
DOWNLOAD_BASE_DIR = "data/packages"
NUM_WORKERS = PACKAGE_DOWNLOAD_THREADS  # 下载线程数量

class PackagesDownloader:
    """
    从 packages.json 读取包信息，并多线程下载过期包
    """

    def __init__(self, json_path: str = PACKAGES_JSON_PATH, download_dir: str = DOWNLOAD_BASE_DIR):
        self.progress = None    
        self.json_path = json_path
        self.download_dir = download_dir
        self.lock = threading.Lock()  # 保护内存 packages_data
        self.packages_data: Dict[str, dict] = {}  # 内存中的包数据

    def load_packages(self):
        """从 JSON 文件加载包数据"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.packages_data = json.load(f)
            log.info(f"加载 {len(self.packages_data)} 个包的数据")
        except FileNotFoundError:
            log.error(f"{self.json_path} 不存在")
            self.packages_data = {}

    def save_packages(self):
        """将内存中的包数据保存回 JSON 文件"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.packages_data, f, indent=2, ensure_ascii=False)
            log.info(f"包信息已保存到 {self.json_path}")
        except Exception as e:
            log.error(f"保存包信息失败: {e}")


    def download_package(self, thread_name: str, package_name: str, version: str, filename: str, url: str, sha256: str) -> bool:
        """
        下载单个包到指定目录，并在内存中更新 status
        增加哈希验证与失败重试机制

        Args:
            worker_id: 线程ID
            package_name: 包名
            version: 包版本
            filename: 下载文件名
            url: 下载地址
            sha256: 期望的SHA256哈希值
        """
        target_dir = os.path.join(self.download_dir, package_name, version)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)

        def calc_sha256(path: str) -> str:
            """计算文件的SHA256"""
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        MAX_RETRY = 3
        for attempt in range(1, MAX_RETRY + 1):
            try:
                log.debug(f"线程 {thread_name} 第({attempt}/{MAX_RETRY})次尝试下载 {filename}")
                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # 验证哈希
                if sha256:
                    file_hash = calc_sha256(file_path)
                    if file_hash.lower() != sha256.lower():
                        raise ValueError(f"哈希不匹配 (expected {sha256}, got {file_hash})")

                log.debug(f"线程 {thread_name} 成功下载并验证 {filename}")

                # 更新进度条
                with self.lock:
                    if self.progress:
                        self.progress.update(1)

                return True

            except Exception as e:
                log.warning(f"线程 {thread_name} 下载 {filename} 第 {attempt} 次失败: {e}")
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        log.warning(f"无法删除损坏文件 {file_path}")
                if attempt < MAX_RETRY:
                    continue
                else:
                    log.error(f"线程 {thread_name} 下载 {filename} 连续失败 {MAX_RETRY} 次，放弃")

                    # 更新进度条
                    with self.lock:
                        if self.progress:
                            self.progress.update(1)
                            
                    return False


    def worker_thread(self, worker_id: int, packages_data: dict):
        """工作线程函数，处理分配的包"""

        thread_name = f"Worker-{worker_id}"
        for package_name, info in packages_data.items():
            last_downloaded_version = info["last_downloaded_version"]
            failed = False  # 标记包是否失败
            for version, releases in info["latest_releases"].items():
                for filename, file_info in releases.items():
                    success = self.download_package(thread_name, package_name, version, filename, file_info["url"], file_info["sha256"])
                    if not success:
                        failed = True
                        break  # 任意文件失败，跳出当前版本循环
                    else:
                        last_downloaded_version = version
                if failed:
                    break  # 任意文件失败，跳出所有版本循环

            # 下载完该包后处理状态
            package_dir = os.path.join(self.download_dir, package_name, version)
            with self.lock:
                if failed:
                    # 删除下载失败的版本的目录，并保持 status 为 outdated
                    if os.path.exists(package_dir):
                        shutil.rmtree(package_dir)
                        log.warning(f"线程 {thread_name} 下载 {package_name} 失败，保留版本 {last_downloaded_version} ，状态 outdated")
                else:
                    # 全部文件下载成功，更新 status
                    info['status'] = 'up_to_date'
                    log.debug(f"线程 {thread_name} 下载 {package_name} 成功，状态 up_to_date")
                info['last_downloaded_version'] = last_downloaded_version

        log.info(f"{thread_name} 完成所有任务")
    
    def clear_directory(self, folder_path: str = "data/packages") -> bool:
        """
        删除目录下所有内容，保留目录
        """
        if not os.path.exists(folder_path):
            log.warning(f"目录不存在: {folder_path}")
            return False
        
        try:
            # 先删除整个目录
            shutil.rmtree(folder_path)
            # 然后重新创建空目录
            os.makedirs(folder_path)
            
            log.info(f"成功清空目录: {folder_path}")
            return True
            
        except Exception as e:
            log.error(f"清空目录失败 {folder_path}: {e}")
            return False

    def download_outdated_packages(self):
        """
        多线程下载所有 status 为 outdated 的包
        """

        # 清除所有旧数据
        self.clear_directory()
           
        # 筛选所有 outdated 包
        outdated_packages = {name: info for name, info in self.packages_data.items() 
                    if info.get("status") == "outdated"}
        

        # 统计需要下载的文件总数
        total_files = 0
        for info in outdated_packages.values():
            for version, releases in info["latest_releases"].items():
                total_files += len(releases)

        # 创建全局进度条
        self.progress = tqdm(total=total_files, desc="下载进度", ncols=80)

        
        """
        将字典按键平均分配到多个列表中
        """
        all_keys = list(outdated_packages.keys())
        total_items = len(all_keys)
        items_per_worker = total_items // NUM_WORKERS
        remainder = total_items % NUM_WORKERS
        
        workloads = []
        start_idx = 0
        
        for i in range(NUM_WORKERS):
            # 计算当前线程应该处理的项目数
            current_items = items_per_worker + (1 if i < remainder else 0)
            end_idx = start_idx + current_items
            
            # 提取对应的键，然后构建子字典
            worker_keys = all_keys[start_idx:end_idx]
            worker_dict = {k: outdated_packages[k] for k in worker_keys}
            workloads.append(worker_dict)
            
            start_idx = end_idx


        log.info("=" * 50)
        log.info("开始多线程包下载")
        log.info(f"工作分配: {len(workloads)} 线程")
        log.info("=" * 50)
        
        # 创建并启动工作线程
        threads = []
        start_time = time.time()
        
        for i, workload in enumerate(workloads):
            if workload:  # 只创建有工作的线程
                thread = threading.Thread(
                    target=self.worker_thread,
                    args=(i + 1, workload,)
                )
                threads.append(thread)
                thread.start()
        
        # 等待所有工作线程完成
        for thread in threads:
            thread.join()

        end_time = time.time()
        log.info(f"多线程处理完成，耗时: {end_time - start_time:.2f}秒")

        # 所有包下载完成后保存数据
        self.save_packages()


# --------------------------
# 模块入口
# --------------------------
def main():
    downloader = PackagesDownloader()
    downloader.load_packages()
    downloader.download_outdated_packages()
