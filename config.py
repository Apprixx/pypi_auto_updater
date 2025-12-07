import sys 

# 测试模式 True or False
DEBUG_MODE = False

# 下载策略："whitelist"（白名单）或 "blacklist"（黑名单）
DOWNLOAD_MODE = "whitelist"

# 平台列表名单（遵循下载策略）["windows", "mac", "linux"]
PLATFORMS_LIST = ["windows", "linux"]

# 各平台关键词匹配表
PLATFORM_KEYWORDS = {
    "windows": ["win32", "win64", "windows", "pywin", "pypiwin32"],
    "mac": ["mac", "osx", "darwin"],
    "linux": ["linux", "ubuntu", "debian", "centos", "fedora"],
}

# 并发线程配置
VERSION_CHECK_THREADS = 10
PACKAGE_DOWNLOAD_THREADS = 2

# 若无法识别平台，是否仍允许下载
ALLOW_UNKNOWN_PLATFORM_DOWNLOAD = True

# 开关SSL验证
VERIFY_SSL = False

# windows计划任务每天运行时间
START_TIME = "03:00"

def check_config():
    if DOWNLOAD_MODE not in ["whitelist","blacklist"]:
        print(f"错误的下载策略:{DOWNLOAD_MODE} 应为 whitelist blacklist 之一")
        sys.exit()

    for platform in PLATFORMS_LIST:
        if platform.lower() not in ["windows", "mac", "linux"]:
            print(f"无效平台{platform} 应为 windows mac linux 之一")
            sys.exit()

