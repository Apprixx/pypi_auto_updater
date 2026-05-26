# PyPI 自动更新工具

一个运行于 Windows 平台的自动化工具，用于：

- 定期检查并下载指定 PyPI 包的最新版本
- 自动同步 Microsoft Defender 最新病毒定义
- 为离线环境 / 内网环境构建本地 Python 包镜像与病毒库
- 支持 Windows 计划任务每日自动执行

---

# 功能特性

## PyPI 包自动更新

支持约 1600 个 Python 包的自动更新：

- 从 `init_packages.json` 读取待监控包列表
- 调用 PyPI JSON API 获取最新版本
- 与本地版本数据进行比对
- 自动筛选 Windows / Linux 平台文件
- 优先使用国内镜像源下载
- 自动回退官方 CDN
- SHA-256 文件完整性校验
- 自动 ZIP 归档每日下载内容

### 下载流程

```text
PyPI API 查询
    ↓
版本比对
    ↓
筛选平台文件
    ↓
镜像源下载
    ↓
SHA-256 校验
    ↓
ZIP 归档
```

---

## Microsoft Defender 病毒定义同步

自动下载并维护最新 Defender 病毒定义：

- 下载 `mpam-fe.exe`
- 使用 `pefile` 解析 PE 文件版本号
- 与本地版本记录比较
- 自动保留最新版本

---

# 项目结构

```text
project/
├── main.py
├── config.py
├── defender_update.py
├── init_packages.json
├── run.bat
├── create_scheduled_task.py
├── create_scheduled_task.bat
├── delete_scheduled_task.bat
│
├── core/
│   ├── package_manager.py
│   ├── version_checker.py
│   ├── version_updater.py
│   ├── packages_downloader.py
│   └── platform_analyser.py
│
├── utils/
│   ├── logger.py
│   ├── init_packages.py
│   ├── archive_generator.py
│   └── remove_empty_folders.py
│
├── data/
│   ├── packages.json
│   ├── archives/
│   └── logs/
```

---

# 核心模块说明

| 文件 | 说明 |
|---|---|
| `main.py` | 主入口文件 |
| `config.py` | 全局配置 |
| `defender_update.py` | Defender 更新模块 |
| `core/package_manager.py` | 多线程版本检查调度 |
| `core/version_checker.py` | PyPI API 查询 |
| `core/version_updater.py` | 版本比对 |
| `core/packages_downloader.py` | 多线程下载器 |
| `core/platform_analyser.py` | 平台文件筛选 |
| `utils/logger.py` | 日志系统 |
| `utils/archive_generator.py` | ZIP 归档生成 |
| `utils/remove_empty_folders.py` | 清理空目录 |

---

# 执行流程

项目运行时执行顺序：

1. 校验配置
2. 初始化包列表
3. 多线程检查版本
4. 保存检查结果
5. 多线程下载更新
6. 清理空目录
7. 生成 ZIP 归档
8. 更新 Defender 病毒定义

---

# 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `DEBUG_MODE` | `False` | 调试日志开关 |
| `DOWNLOAD_MODE` | `whitelist` | 下载模式 |
| `PLATFORMS_LIST` | `["windows", "linux"]` | 目标平台 |
| `VERSION_CHECK_THREADS` | `10` | 版本检查线程数 |
| `PACKAGE_DOWNLOAD_THREADS` | `2` | 下载线程数 |
| `ALLOW_UNKNOWN_PLATFORM_DOWNLOAD` | `True` | 下载未知平台文件 |
| `VERIFY_SSL` | `False` | SSL 验证 |
| `DROP404` | `True` | 跳过不存在包 |
| `SKIP_EMPTY_ZIP` | `True` | 无文件时跳过归档 |
| `START_TIME` | `03:00` | 定时执行时间 |

---

# 安装依赖

## Python 依赖

```bash
pip install requests
pip install tqdm
pip install packaging
pip install pefile
```

---

# 使用方法

## 手动运行

```bash
python main.py
```

或：

```bash
run.bat
```

---

## 创建计划任务

运行：

```bash
create_scheduled_task.bat
```

或：

```bash
python create_scheduled_task.py
```

默认每天凌晨 `03:00` 自动执行。

---

## 删除计划任务

```bash
delete_scheduled_task.bat
```

---

# 数据模型

`data/packages.json` 示例：

```json
{
  "absl-py": {
    "last_checked": "2026-05-19T03:06:58.116170",
    "last_downloaded_version": "2.4.0",
    "latest_version": "2.4.0",
    "status": "up_to_date",
    "latest_releases": {}
  }
}
```

## 状态值说明

| 状态 | 含义 |
|---|---|
| `null` | 未检查 |
| `up_to_date` | 已是最新版本 |
| `outdated` | 存在新版本 |
| `404` | PyPI 不存在该包 |
| `Network Error` | 网络错误 |
| `Timeout` | 请求超时 |
| `ConnectionError` | 连接失败 |
| `HTTPError` | HTTP 错误 |
| `ignore` | 忽略该包 |

---

# 镜像源策略

优先尝试国内镜像：

- USTC
- 腾讯云
- 华为云
- 阿里云
- 清华大学

策略特点：

- 随机镜像顺序
- 每个镜像最多重试 3 次
- 自动回退官方 CDN
- 每次下载进行 SHA-256 校验

---

# 日志系统

日志目录：

```text
data/logs/
```

日志内容：

- 普通运行日志
- Defender 更新日志
- 控制台实时输出
- DEBUG 调试信息

日志文件命名：

```text
log_YYYYMMDD_HHMMSS.txt
```

---

# 注意事项

- 当前仅支持 Windows
- 依赖 Windows Task Scheduler
- `VERIFY_SSL=False` 不建议用于生产环境
- `init_packages.json` 需要手动维护
- 建议定期清理 `data/archives/`
- 项目当前未提供 `requirements.txt`

---

# 适用场景

- 内网 Python 包镜像
- 离线环境依赖同步
- 企业软件仓库缓存
- Defender 病毒库离线更新
- 自动化运维环境

---

# License

MIT License
