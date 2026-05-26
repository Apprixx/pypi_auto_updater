import threading
import time
import json
import queue
from typing import Dict, Any, Optional
from utils.init_packages import initialize_packages
from utils.logger import log
from core.version_checker import VersionChecker
from core.version_updater import VersionUpdater
from core.packages_downloader import main as packages_downloader
from config import VERSION_CHECK_THREADS
from config import DROP404

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


def worker_thread_dynamic(worker_id: int, package_manager: PackageManager, task_queue: queue.Queue):
    """
    动态领取任务的 Worker 线程函数
    """

    thread_name = f"Worker-{worker_id}"
    log.info(f"{thread_name} 启动，等待任务...")

    while True:
        try:
            # 动态领取一个任务包名
            package_name = task_queue.get_nowait()
        except queue.Empty:
            log.info(f"{thread_name} 任务领取完毕，退出")
            return

        log.debug(f"{thread_name} 领取任务: {package_name}")

        try:
            # === 以下保持与你现有代码完全一致 ===
            version_checker = VersionChecker(package_name, thread_name)
            if not DROP404 or package_manager.packages_data[package_name].get('status') != '404':
                pypi_info, status = version_checker.get_package_info_from_pypi()

                version_updater = VersionUpdater(
                    pypi_info,
                    package_manager,
                    package_name,
                    status
                )
                err = version_updater.process_package_info()

                if err:
                    log.error(f"{thread_name} 处理 {package_name} 失败:{err}")
                else:
                    log.debug(f"{thread_name} 更新 {package_name} 完成")

        except Exception as e:
            log.exception(f"{thread_name} 处理 {package_name} 时发生异常: {e}")

        finally:
            # 通知队列：我完成了一个任务
            task_queue.task_done()


def load_from_file(path: str = "data/packages.json") -> Dict[str, Any]:
    """
    单线程从文件加载数据（不需要锁）
    """
    initialize_packages()
    # try:
    #     with open(path, 'r', encoding='utf-8') as f:
    #         return json.load(f)
    # except FileNotFoundError:
    #     log.info(f"packages.json 不存在，开始初始化...")
    #     # 初始化后重新读取
    #     with open(path, 'r', encoding='utf-8') as f:
    #         return json.load(f)
    with open(path, 'r', encoding='utf-8') as f:
        packages = json.load(f)
    return packages
    # if DROP404:
    #     drop_packages = {k: v for k, v in packages.items() if (v or {}).get('status') != '404'}
    #     log.info(f"要求【DROP404】，已跳过")


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
    import queue
    import threading
    import time

    # 单线程：从文件加载数据
    packages_data = load_from_file()
    log.info(f"从文件加载了 {len(packages_data)} 个包的数据")
    
    # 创建包管理器（管理内存中的数据）
    package_manager = PackageManager(packages_data)
    
    # ==== 使用 Queue 实现动态任务分配 ====
    task_queue = queue.Queue()

    # 将所有任务放入队列
    for pkg in packages_data.keys():
        task_queue.put(pkg)

    log.info("=" * 50)
    log.info("开始多线程包信息更新（动态工作分配模式）")
    log.info(f"总任务数: {task_queue.qsize()} | 线程数: {NUM_WORKERS}")
    log.info("=" * 50)

    # ==== 创建工作线程 ====
    threads = []
    start_time = time.time()

    for worker_id in range(1, NUM_WORKERS + 1):
        t = threading.Thread(
            target=worker_thread_dynamic,
            args=(worker_id, package_manager, task_queue)
        )
        t.daemon = True
        threads.append(t)
        t.start()

    # 等待队列任务全部完成
    task_queue.join()

    # # 分配工作给线程
    # all_packages = list(packages_data.keys())
    # num_workers = NUM_WORKERS
    # packages_per_worker = len(all_packages) // num_workers
    
    # workloads = []
    # for i in range(num_workers):
    #     start_idx = i * packages_per_worker
    #     if i == num_workers - 1:  # 最后一个线程处理剩余的所有包
    #         workloads.append(all_packages[start_idx:])
    #     else:
    #         workloads.append(all_packages[start_idx:start_idx + packages_per_worker])
    
    # log.info("=" * 50)
    # log.info("开始多线程包信息更新")
    # log.info(f"工作分配: {len(workloads)} 线程")
    # log.info("=" * 50)
    
    # # 创建并启动工作线程
    # threads = []
    # start_time = time.time()
    
    # for i, workload in enumerate(workloads):
    #     if workload:  # 只创建有工作的线程
    #         thread = threading.Thread(
    #             target=worker_thread,
    #             args=(i + 1, package_manager, workload)
    #         )
    #         threads.append(thread)
    #         thread.start()
    
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

