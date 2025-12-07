from datetime import datetime
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import log
from core.platform_analyser import PlatformAnalyser


"""
例子：
pypi_info:
{
    "info": 
    {
        "requires_python": "\u003E=3.9",
        "summary": "Powerful data structures for data analysis, time series, and statistics",
        "version": "2.3.3",
        "yanked": false,
        "yanked_reason": null
    },
    "releases": 
    {
        2.3.2": 
        [   
            {
                "comment_text": null,
                "digests": 
                {
                    "blake2b_256": "2e16a8eeb70aad84ccbf14076793f90e0031eded63c1899aeae9fdfbf37881f4",
                    "md5": "321934f82f2d2bf34ae341c5352065fa",
                    "sha256": "52bc29a946304c360561974c6542d1dd628ddafa69134a7131fdfd6a5d7a1a35"
                },
                "downloads": -1,
                "filename": "pandas-2.3.2-cp310-cp310-macosx_10_9_x86_64.whl",
                "has_sig": false,
                "md5_digest": "321934f82f2d2bf34ae341c5352065fa",
                "packagetype": "bdist_wheel",
                "python_version": "cp310",
                "requires_python": "\u003E=3.9",
                "size": 11539648,
                "upload_time": "2025-08-21T10:26:36",
                "upload_time_iso_8601": "2025-08-21T10:26:36.236532Z",
                "url": "https://files.pythonhosted.org/packages/2e/16/a8eeb70aad84ccbf14076793f90e0031eded63c1899aeae9fdfbf37881f4/pandas-2.3.2-cp310-cp310-macosx_10_9_x86_64.whl",
                "yanked": false,
                "yanked_reason": null
            }
        ]
    }
}
"""

class VersionUpdater():
    def __init__(self, pypi_info, package_manager, package_name, status):
        if not status:
            self.latest_version = pypi_info["info"]["version"]
            self.releases = pypi_info["releases"]

        self.last_downloaded_version = package_manager.packages_data[package_name]["last_downloaded_version"]
        self.package_manager = package_manager
        self.package_name = package_name
        self.status = status


    def get_new_versions(self, last_downloaded_version):
        """
        将旧版本到最新正式版之间所有版本（包括最新）添加到new_versions中
        """
        # 获取所有键的列表
        keys = list(self.releases.keys())

        # 找到旧版本和新版本的位置
        start_index = keys.index(last_downloaded_version)
        end_index = keys.index(self.latest_version)

        # 获取这两个位置之间的所有键（包含最新正式版）
        target_keys = keys[start_index + 1:end_index + 1]

        # 返回新版本字典
        return {k: self.releases[k] for k in target_keys}


    def process_package_info(self) -> Optional[Dict[str, Any]]:
        """
        更新单个包的信息（线程安全操作）
        """
        # 从PyPI获取最新信息
        with self.package_manager.lock:
            if self.status:
                # 如果在获取包信息时出现错误直接跳过
                status = self.status
                result = {
                "last_checked": datetime.now().isoformat(),
                "status": status,
                }
                self.package_manager.packages_data[self.package_name].update(result)
            
            elif self.last_downloaded_version == self.latest_version:
                # 如果无新版本则不更新
                self.package_manager.packages_data[self.package_name].update({"last_checked": datetime.now().isoformat()})

            else:
                status = "outdated" 
                if self.last_downloaded_version:
                    # 将添加新版本
                    new_versions = self.get_new_versions(self.last_downloaded_version)
                else:
                    # 如果是第一次则直接用最新覆盖
                    new_versions = {self.latest_version: self.releases[self.latest_version]}

                # 根据包文件名称判断是否下载
                releases = {}
                for version, all_releases in new_versions.items():
                    for one_release in all_releases:        
                        filename = one_release["filename"]
                        platform_analyser = PlatformAnalyser(filename)
                        if platform_analyser.should_download():
                            # 如果version键不存在，自动创建空字典
                            releases.setdefault(version, {})[filename] = {"url":one_release["url"],"sha256":one_release["digests"]["sha256"]}

                # 更新内存中的数据
                result = {
                    "last_checked": datetime.now().isoformat(),
                    "latest_version": self.latest_version,
                    "status": status,
                    "latest_releases": releases
                }
                self.package_manager.packages_data[self.package_name].update(result)
                        
        return self.status
