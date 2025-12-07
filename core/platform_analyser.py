from utils.logger import log
from config import (
    DOWNLOAD_MODE,
    PLATFORMS_LIST,
    PLATFORM_KEYWORDS,
    ALLOW_UNKNOWN_PLATFORM_DOWNLOAD,
)


class PlatformAnalyser:
    """根据包名分析平台并判断是否允许下载"""

    def __init__(self, filename: str):
        self.download_mode = DOWNLOAD_MODE.lower().strip()  # "whitelist" or "blacklist"
        self.platforms_list = [p.lower() for p in PLATFORMS_LIST]
        self.keywords = PLATFORM_KEYWORDS
        self.allow_unknown = bool(ALLOW_UNKNOWN_PLATFORM_DOWNLOAD)
        self.filename = filename

    def analyse_platform(self) -> str | None:
        """根据包名推测平台"""
        if not self.filename or not isinstance(self.filename, str):
            return None

        name = self.filename.lower()

        for platform, keywords in self.keywords.items():
            for kw in keywords:
                if kw in name:
                    if platform == "mac" and name.startswith("machine"):
                        continue  # 避免误判
                    return platform
        return None


    def should_download(self) -> bool:
        """
        判断是否应下载此包。
        返回 True 表示允许下载，False 表示跳过。
        """
        platform = self.analyse_platform()
        if platform is None:
            log.debug(f"无法判断平台，{'默认下载' if self.allow_unknown else '默认不下载'}")
            return self.allow_unknown

        if self.download_mode == "whitelist":
            log.debug(f"白名单模式，检查平台 {platform} 是否在白名单 {self.platforms_list} 中")
            return platform in self.platforms_list
        
        elif self.download_mode == "blacklist":
            log.debug(f"黑名单模式，检查平台 {platform} 是否在黑名单 {self.platforms_list} 中")
            return platform not in self.platforms_list



