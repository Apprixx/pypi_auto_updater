import requests
import time
import urllib3
from typing import Dict, Any, Optional
from utils.logger import log
from config import VERIFY_SSL

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VersionChecker():
    def __init__(self,package_name, thread_name):
        self.package_name = package_name
        self.thread_name = thread_name

    def get_package_info_from_pypi(self) -> Optional[Dict[str, Any]]:
        """
        从PyPI获取包的最新信息（手动重试机制）
        """
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        max_retries = 3
        retry_delay = 1  # 初始延迟秒数
        
        for attempt in range(max_retries):
            try:
                log.debug(f"线程 {self.thread_name} 正在获取 {self.package_name} 的信息 (尝试 {attempt + 1}/{max_retries})")
                response = requests.get(url, verify = VERIFY_SSL, timeout=8)
                response.raise_for_status()
                
                data = response.json()
                log.debug(f"线程 {self.thread_name} 成功获取 {self.package_name} 的信息")
                
                return data, None
                
            except requests.exceptions.ConnectionError as e:
                log.warning(f"连接错误 ({attempt + 1}/{max_retries}): SSL连接中断错误")
                if attempt < max_retries - 1:  # 不是最后一次尝试
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                else:
                    log.error(f"获取 {self.package_name} 信息失败，已达到最大重试次数")
                    return None, "Network Error"
                    
            except requests.exceptions.Timeout as e:
                log.warning(f"请求超时 ({attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    log.error(f"获取 {self.package_name} 信息失败，请求超时")
                    return None, "Network Error"
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 500, 502, 503, 504]:  # 可重试的HTTP错误
                    log.warning(f"HTTP错误 ({attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        log.error(f"获取 {self.package_name} 信息失败，HTTP错误")
                        return None, "Network Error"
                else:
                    # 其他HTTP错误（如404）不重试
                    log.error(f"获取 {self.package_name} 信息失败: {e}")
                    return None, "ignore"
                    
            except Exception as e:
                log.error(f"获取 {self.package_name} 信息失败: {e}")
                return None, "Network Error"  # 其他异常不重试
