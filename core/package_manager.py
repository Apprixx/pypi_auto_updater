import threading
import time
import json
from typing import Dict, Any, Optional
from utils.init_packages import initialize_packages
from utils.logger import log
from core.version_checker import VersionChecker
from core.version_updater import VersionUpdater
from core.packages_downloader import main as packages_downloader
from config import VERSION_CHECK_THREADS

NUM_WORKERS = VERSION_CHECK_THREADS

class PackageManager:
    """
    包管理器 - 只负责内存中包数据的线程安全操作
    """
    
    def __init__(self, initial_data: Dict[str, Any]):
        """
        初始化包管理器
        
        Args:
            initial_data: 初始的包数据
        """
        self.packages_data = initial_data
        self.lock = threading.Lock()  # 只保护内存中的packages_data
    
    def get_packages_data(self) -> Dict[str, Any]:
        """
        获取当前包数据（线程安全）
        """
        with self.lock:
            return self.packages_data.copy()  # 返回拷贝避免外部修改
        
        
def worker_thread(worker_id: int, package_manager: PackageManager, packages_to_process: list):
    """
    工作线程函数 - 处理分配的包
    """
    thread_name = f"Worker-{worker_id}"
    
    log.info(f"{thread_name} 开始处理 {len(packages_to_process)} 个包")
    
    for package_name in packages_to_process:
        version_checker = VersionChecker(package_name, thread_name)
        pypi_info, status = version_checker.get_package_info_from_pypi()

        version_updater = VersionUpdater(pypi_info, package_manager, package_name, status)
        err = version_updater.process_package_info()

        if err:
            log.error(f"线程 {thread_name} 处理 {package_name} 失败:{err}")
        else:
            log.debug(f"线程 {thread_name} 更新 {package_name} 完成")
    
    log.info(f"{thread_name} 完成所有任务")


def load_from_file(path: str = "data/packages.json") -> Dict[str, Any]:
    """
    单线程从文件加载数据（不需要锁）
    """
    initialize_packages()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        log.info(f"packages.json 不存在，开始初始化...")
        # 初始化后重新读取
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_to_file(data: Dict[str, Any], filepath: str = "data/packages.json"):
    """
    单线程保存数据到文件（不需要锁）
    """
    log.info("开始保存数据到文件...")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log.info(f"数据已保存到 {filepath}")
    except Exception as e:
        log.error(f"保存文件失败: {e}")


def run_package_workflow():
    """主函数 入口 - 协调多线程处理和单线程文件操作"""
    
    # 单线程：从文件加载数据
    packages_data = load_from_file()
    log.info(f"从文件加载了 {len(packages_data)} 个包的数据")
    
    # 创建包管理器（管理内存中的数据）
    package_manager = PackageManager(packages_data)
    
    # 分配工作给线程
    all_packages = list(packages_data.keys())
    num_workers = NUM_WORKERS
    packages_per_worker = len(all_packages) // num_workers
    
    workloads = []
    for i in range(num_workers):
        start_idx = i * packages_per_worker
        if i == num_workers - 1:  # 最后一个线程处理剩余的所有包
            workloads.append(all_packages[start_idx:])
        else:
            workloads.append(all_packages[start_idx:start_idx + packages_per_worker])
    
    log.info("=" * 50)
    log.info("开始多线程包信息更新")
    log.info(f"工作分配: {len(workloads)} 线程")
    log.info("=" * 50)
    
    # 创建并启动工作线程
    threads = []
    start_time = time.time()
    
    for i, workload in enumerate(workloads):
        if workload:  # 只创建有工作的线程
            thread = threading.Thread(
                target=worker_thread,
                args=(i + 1, package_manager, workload)
            )
            threads.append(thread)
            thread.start()
    
    # 等待所有工作线程完成
    for thread in threads:
        thread.join()
    
    # 多线程处理完成
    end_time = time.time()
    log.info(f"多线程处理完成，耗时: {end_time - start_time:.2f}秒")
    
    # 单线程：获取最终数据并保存到文件
    final_data = package_manager.get_packages_data()
    
    # 单线程：保存到文件
    save_to_file(final_data)
    
    # 下载过期的包
    packages_downloader()

