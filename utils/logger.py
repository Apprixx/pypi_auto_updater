import os
from datetime import datetime
from config import DEBUG_MODE

class logger():
    def __init__(self, log_file=None, log_level="DEBUG" if DEBUG_MODE else "INFO"):
        """
        初始化日志器
        
        Args:
            log_file (str): 日志文件路径，如果为None则使用默认路径
            log_level (str): 日志级别，可选 DEBUG, INFO, WARNING, ERROR
        """
        # 设置日志级别映射
        self.log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        self.current_level = log_level.upper()
        
        # 设置日志文件路径 - 根目录下的 data/logs 文件夹
        if log_file is None:
            # 根目录下的 data/logs 文件夹
            log_dir = "data/logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(log_dir, f"log_{current_time}.txt")
        else:
            self.log_file = log_file
            
        # 确保日志文件目录存在
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        print(f"日志文件路径: {self.log_file}")

    def _write_log(self, level, message):
        """内部方法：写入日志到文件和控制台"""
        if self.log_levels[level] < self.log_levels[self.current_level]:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # 输出到控制台
        print(log_message)
        
        # 写入到文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"写入日志文件失败: {e}")

    def error(self, message):
        """错误级别日志"""
        self._write_log("ERROR", message)

    def info(self, message):
        """信息级别日志"""
        self._write_log("INFO", message)

    def warning(self, message):
        """警告级别日志"""
        self._write_log("WARNING", message)
    
    def debug(self, message):
        """调试级别日志"""
        self._write_log("DEBUG", message)

    def set_level(self, level):
        """设置日志级别"""
        level = level.upper()
        if level in self.log_levels:
            self.current_level = level
            self.info(f"日志级别已设置为: {level}")
        else:
            print(f"无效的日志级别: {level}")

log = logger()
