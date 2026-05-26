import json
import logging
import os
from pathlib import Path
import requests
from datetime import datetime
import xml.etree.ElementTree as ET

# -------------------------------
# 配置
# -------------------------------
XML_URL = "https://go.microsoft.com/fwlink/?LinkID=121721"  # 官方病毒库 XML 信息
URL = "https://go.microsoft.com/fwlink/?LinkID=121721&arch=x64"
SAVE_DIR = r"data/archives/"
LATEST_JSON = "data/archives/latest.json"
LOG_FILE = "data/logs/defender_update.log"

# -------------------------------
# 日志配置
# -------------------------------
logging.basicConfig(filename=LOG_FILE,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    level=logging.INFO, encoding='utf-8')

def log(msg):
    print(msg)
    logging.info(msg)


def get_defender_exe_version(file_path: str) -> str:
    import pefile
    from pathlib import Path

    file_path = Path(file_path)
    pe = pefile.PE(str(file_path))

    version = None

    # 遍历 FileInfo 的所有层级
    if hasattr(pe, 'FileInfo') and pe.FileInfo:
        for fileinfo in pe.FileInfo:
            # fileinfo 可能是 list，也可能是对象
            if isinstance(fileinfo, list):
                candidates = fileinfo
            else:
                candidates = [fileinfo]
            for info in candidates:
                if hasattr(info, "Key") and info.Key == b"StringFileInfo":
                    for st in info.StringTable:
                        for key, value in st.entries.items():
                            k = key.decode(errors="ignore")
                            v = value.decode(errors="ignore")
                            if k in ("FileVersion", "ProductVersion"):
                                version = v
                                break

    pe.close()
    if not version:
        raise RuntimeError("未在 mpam-fe.exe 中找到版本信息")

    # 清理格式：1,425,1234,0 → 1.425.1234.0
    version = version.replace(",", ".").strip()

    return version


# -------------------------------
# 读取本地最新版本（如没有则返回 None）
# -------------------------------
def load_local_version():
    if not os.path.exists(LATEST_JSON):
        return None
    try:
        with open(LATEST_JSON, "r", encoding="utf-8") as f:
            return json.load(f)["latest_version"]
    except Exception:
        return None


# -------------------------------
# 保存最新版本到 JSON
# -------------------------------
def save_local_version(version):
    with open(LATEST_JSON, "w", encoding="utf-8") as f:
        json.dump({"latest_version": version}, f, indent=4)


# -------------------------------
# 下载文件
# -------------------------------
def download_update(url):
    os.makedirs(str(Path(SAVE_DIR)), exist_ok=True)

    file_name = f"mpam-fe_0.exe"
    file_path = Path(SAVE_DIR) / file_name

    log(f"开始下载：{file_name}…")

    with requests.get(url, stream=True, timeout=7200) as r:
    # with requests.get(url, verify=False, stream=True, timeout=7200) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    log(f"下载完成：{file_path}")
    return file_path


# -------------------------------
# 主程序
# -------------------------------
def main():
    log("========== Defender 更新程序启动 ==========")

    # latest_version, download_url = fetch_latest_info()
    # log(f"微软最新版本号：{latest_version}")
    # log(f"下载链接：{download_url}")

    last_local = load_local_version()
    log(f"本地记录的上次版本号：{last_local}")

    # if last_local == latest_version:
    #     log("检测到无新版本，跳过下载。")
    #     log("========== 程序结束 ==========\n")
    #     return

    latest_version = '0'  # 临时给个版本号，下载后再改名
    file_path = download_update(URL)

    log("开始获取下载到的病毒库文件的版本号…")
    version = get_defender_exe_version(file_path)

    if last_local == version:
        # 版本与上次下载到的版本一致，无需操作，应删除刚刚下载的病毒库文件
        os.remove(file_path)
        log("下载到的病毒库文件的版本号{version}与上次下载的版本一致，已删除它")
    else:
        # 版本不一致，则需要重命名文件，并记录本次下载的版本号
        new_path = Path(SAVE_DIR) / f"mpam-fe_{version}.exe"
        os.rename(file_path, new_path)
        save_local_version(version)
        log(f"下载到新的病毒库文件：{new_path}，已更新本地记录版本号：{version}")

    log("========== 更新完成，程序结束 ==========\n")


if __name__ == "__main__":
    main()
