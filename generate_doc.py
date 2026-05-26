"""Generate project documentation as a .docx file (no external dependencies)."""

import zipfile
import os
import textwrap

PROJECT_DIR = r"D:\now\pypi_auto_updater"
OUTPUT = os.path.join(PROJECT_DIR, "项目文档.docx")

# --- Content sections ---
sections = []  # list of (heading_level, text_or_list_items)

def add_heading(text, level=1):
    sections.append(("heading", (level, text)))

def add_paragraph(text):
    sections.append(("paragraph", text))

def add_table(headers, rows):
    sections.append(("table", (headers, rows)))

def add_bullet_list(items):
    sections.append(("list", items))

# ===== Document Content =====

add_heading("PyPI 自动更新工具 — 项目文档", 1)

add_heading("1. 项目概述", 2)
add_paragraph(
    "本项目是一个运行于 Windows 平台的自动化工具，用于定期检查并下载 PyPI 仓库中指定 Python 包的最新版本，"
    "同时自动下载 Microsoft Defender 最新病毒定义文件。项目通过 Windows 计划任务实现每日定时执行，"
    "旨在为离线或内网环境构建本地化的 Python 包镜像和病毒定义库。"
)

add_heading("2. 功能模块", 2)

add_heading("2.1 PyPI 包自动更新", 3)
add_paragraph(
    "该模块负责监控约 1600 个 Python 包的版本更新，主要流程如下："
)
add_bullet_list([
    "从 init_packages.json 读取待监控的包名列表（约 1,611 个）",
    "通过 PyPI JSON API（https://pypi.org/pypi/<name>/json）查询每个包的最新版本",
    "与本地 data/packages.json 中记录的已下载版本进行比对",
    "对有新版本的包，筛选符合条件的平台文件（Windows/Linux）",
    "优先从国内镜像源（中科大、腾讯云、华为云、阿里云、清华）下载，失败后回退到官方 CDN",
    "下载后通过 SHA-256 哈希校验文件完整性",
    "将当日下载的所有文件压缩为日期命名的 ZIP 归档",
])

add_heading("2.2 Microsoft Defender 病毒定义下载", 3)
add_paragraph(
    "该模块负责下载最新的 Microsoft Defender 病毒定义文件："
)
add_bullet_list([
    "从 Microsoft 官方链接下载 mpam-fe.exe（x64 版本）",
    "使用 pefile 库解析 PE 文件头部获取版本号",
    "与 data/archives/latest.json 中存储的版本进行比对",
    "仅保留新版本文件，文件重命名为 mpam-fe_<版本号>.exe",
])

add_heading("3. 项目结构", 2)

add_table(
    ["路径", "说明"],
    [
        ["main.py", "主入口文件，编排整体执行流程"],
        ["config.py", "全局配置参数"],
        ["defender_update.py", "Microsoft Defender 病毒定义下载模块"],
        ["init_packages.json", "待监控的包名列表（主配置文件）"],
        ["run.bat", "手动运行脚本"],
        ["create_scheduled_task.py", "创建 Windows 计划任务"],
        ["create_scheduled_task.bat", "创建计划任务的批处理封装"],
        ["delete_scheduled_task.bat", "删除计划任务"],
        ["core/package_manager.py", "多线程版本检查调度器"],
        ["core/version_checker.py", "PyPI API 查询模块"],
        ["core/version_updater.py", "版本比对与更新决策模块"],
        ["core/packages_downloader.py", "多线程下载器（含镜像切换与重试）"],
        ["core/platform_analyser.py", "按操作系统平台过滤文件"],
        ["utils/logger.py", "日志记录模块（同时输出到文件和控制台）"],
        ["utils/init_packages.py", "包列表初始化与增量合并"],
        ["utils/archive_generator.py", "ZIP 归档生成器"],
        ["utils/remove_empty_folders.py", "清理空目录工具"],
        ["data/packages.json", "运行时状态数据（包的版本与下载状态）"],
        ["data/archives/", "输出目录（ZIP 归档 + 元数据）"],
        ["data/logs/", "日志目录"],
    ]
)

add_heading("4. 执行流程", 2)
add_paragraph("项目启动后按以下顺序执行各步骤：")
add_bullet_list([
    "步骤 1 — check_config()：校验 DOWNLOAD_MODE 和 PLATFORMS_LIST 配置合法性",
    "步骤 2 — initialize_packages()：将 init_packages.json 增量合并到 data/packages.json",
    "步骤 3 — 多线程版本检查：10 个线程并发查询 PyPI API，比对版本并标记 outdated 状态",
    "步骤 4 — 保存版本检查结果到 data/packages.json",
    "步骤 5 — 多线程下载：2 个线程下载所有状态为 outdated 的包文件",
    "步骤 6 — remove_empty_folders_simple()：清理下载过程中产生的空目录",
    "步骤 7 — archive_generator.main()：将 data/packages/ 下的文件打包为 ZIP 归档",
    "步骤 8 — defender_update.main()：下载并检查 Microsoft Defender 病毒定义",
])

add_heading("5. 配置参数", 2)

add_table(
    ["参数", "默认值", "说明"],
    [
        ["DEBUG_MODE", "False", "调试模式开关，控制日志级别"],
        ["DOWNLOAD_MODE", "whitelist", "下载模式：白名单（仅下载匹配平台的文件）/ 黑名单"],
        ["PLATFORMS_LIST", '["windows", "linux"]', "目标平台列表"],
        ["VERSION_CHECK_THREADS", "10", "版本检查并发线程数"],
        ["PACKAGE_DOWNLOAD_THREADS", "2", "文件下载并发线程数"],
        ["ALLOW_UNKNOWN_PLATFORM_DOWNLOAD", "True", "是否下载无法识别平台的文件"],
        ["VERIFY_SSL", "False", "API 请求是否验证 SSL 证书"],
        ["DROP404", "True", "是否跳过之前返回 404 的包"],
        ["SKIP_EMPTY_ZIP", "True", "无下载内容时是否跳过 ZIP 打包"],
        ["START_TIME", "03:00", "计划任务每日执行时间"],
    ]
)

add_heading("6. 计划任务部署", 2)
add_paragraph(
    "项目通过 Windows Task Scheduler 实现定时执行，部署方式如下："
)
add_bullet_list([
    "创建计划任务：运行 create_scheduled_task.bat（或直接执行 create_scheduled_task.py），"
    "将在系统中注册名为 PyPI_Auto_Updater 的每日任务",
    "默认执行时间：每天凌晨 03:00",
    "执行命令：cmd /c \"cd /d <项目目录> && python main.py\"",
    "删除计划任务：运行 delete_scheduled_task.bat",
    "手动运行：直接执行 run.bat 或 python main.py",
])

add_heading("7. 依赖项", 2)
add_paragraph("项目依赖以下第三方 Python 包：")

add_table(
    ["包名", "用途", "安装命令"],
    [
        ["requests", "HTTP 客户端，用于 API 查询和文件下载", "pip install requests"],
        ["tqdm", "下载进度条显示", "pip install tqdm"],
        ["packaging", "Python 版本号解析与比较", "pip install packaging"],
        ["pefile", "PE 文件解析，用于读取 Defender 病毒定义版本", "pip install pefile"],
    ]
)

add_heading("8. 数据模型", 2)
add_paragraph(
    "data/packages.json 中每条包记录的数据结构示例如下："
)
add_paragraph(
    '{\n'
    '  "absl-py": {\n'
    '    "last_checked": "2026-05-19T03:06:58.116170",\n'
    '    "last_downloaded_version": "2.4.0",\n'
    '    "latest_version": "2.4.0",\n'
    '    "status": "up_to_date",\n'
    '    "latest_releases": { ... }\n'
    '  }\n'
    '}'
)
add_paragraph("状态值说明：")
add_bullet_list([
    "null — 初始状态，尚未检查",
    "up_to_date — 已是最新版本",
    "outdated — 有新版本可用",
    "404 — 包在 PyPI 上不存在",
    "Network Error / Timeout / ConnectionError / HTTPError — 网络错误",
    "ignore — 被忽略的包",
])

add_heading("9. 镜像源策略", 2)
add_paragraph(
    "下载器采用随机优先国内镜像源的策略，以提高下载速度和可靠性："
)
add_bullet_list([
    "优先尝试的国内镜像：USTC、腾讯云、华为云、阿里云、清华大学",
    "每个镜像最多重试 3 次",
    "所有镜像均失败后回退到官方 PyPI CDN（files.pythonhosted.org）",
    "每次下载均进行 SHA-256 哈希校验",
    "镜像选择采用随机顺序（2026-02-18 改为随机策略）",
])

add_heading("10. 日志与监控", 2)
add_bullet_list([
    "日志文件存储在 data/logs/ 目录下，文件名格式为 log_YYYYMMDD_HHMMSS.txt",
    "Defender 更新日志独立存储为 data/logs/defender_update.log",
    "日志同时输出到文件和控制台",
    "DEBUG_MODE 设为 True 时输出详细调试信息",
])

add_heading("11. 注意事项", 2)
add_bullet_list([
    "项目无 requirements.txt，需手动安装上述第三方依赖",
    "VERIFY_SSL 默认为 False，生产环境建议改为 True",
    "init_packages.json 中的包名列表需要手动维护",
    "归档文件存储在 data/archives/ 目录下，需定期清理旧归档以释放磁盘空间",
    "项目当前仅支持 Windows 平台（依赖 Windows Task Scheduler 和 schtasks 命令）",
])


# ===== Generate DOCX =====

def make_run_properties(bold=False, size=None, font=None, color=None):
    parts = []
    if bold:
        parts.append('<w:b/>')
        parts.append('<w:bCs/>')
    if size:
        parts.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    if font:
        parts.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}"/>')
    if color:
        parts.append(f'<w:color w:val="{color}"/>')
    return '<w:rPr>' + ''.join(parts) + '</w:rPr>' if parts else ''

def escape_xml(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def build_paragraph(text, bold=False, size=None, alignment=None):
    pPr = ''
    if alignment:
        pPr = f'<w:jc w:val="{alignment}"/>'
    rpr = make_run_properties(bold=bold, size=size, font="宋体")
    runs = []
    # Split text by newlines, wrap each in <w:t>
    for line in text.split('\n'):
        escaped = escape_xml(line)
        if line == text.split('\n')[0]:
            runs.append(f'{rpr}<w:t xml:space="preserve">{escaped}</w:t>')
        else:
            runs.append(f'<w:br/>{rpr}<w:t xml:space="preserve">{escaped}</w:t>')
    run_xml = ''.join(f'<w:r>{r}</w:r>' for r in runs)
    pPr_xml = f'<w:pPr>{pPr}</w:pPr>' if pPr else ''
    return f'<w:p>{pPr_xml}{run_xml}</w:p>'

def build_heading(level, text):
    escaped = escape_xml(text)
    rpr = make_run_properties(bold=True, size=32 - (level - 1) * 4, font="黑体")
    return f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/></w:pPr><w:r>{rpr}<w:t>{escaped}</w:t></w:r></w:p>'

def build_bullet_list(items):
    xml_parts = []
    for item in items:
        escaped = escape_xml(item)
        rpr = make_run_properties(size=21, font="宋体")
        xml_parts.append(
            f'<w:p>'
            f'<w:pPr>'
            f'<w:pStyle w:val="ListParagraph"/>'
            f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            f'</w:pPr>'
            f'<w:r>{rpr}<w:t>{escaped}</w:t></w:r>'
            f'</w:p>'
        )
    return ''.join(xml_parts)

def build_table(headers, rows):
    # Build table XML
    tbl_xml = '<w:tbl>'
    # Table properties
    tbl_xml += (
        '<w:tblPr>'
        '<w:tblW w:w="5000" w:type="pct"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
        '</w:tblBorders>'
        '</w:tblPr>'
    )
    # Header row
    tbl_xml += '<w:tr>'
    for h in headers:
        escaped = escape_xml(h)
        rpr = make_run_properties(bold=True, size=21, font="宋体")
        tbl_xml += (
            f'<w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/></w:tcPr>'
            f'<w:p><w:r>{rpr}<w:t>{escaped}</w:t></w:r></w:p></w:tc>'
        )
    tbl_xml += '</w:tr>'
    # Data rows
    for row in rows:
        tbl_xml += '<w:tr>'
        for cell in row:
            escaped = escape_xml(cell)
            rpr = make_run_properties(size=21, font="宋体")
            tbl_xml += (
                f'<w:tc><w:p><w:r>{rpr}<w:t>{escaped}</w:t></w:r></w:p></w:tc>'
            )
        tbl_xml += '</w:tr>'
    tbl_xml += '</w:tbl>'
    return tbl_xml


# Build document body
body_xml = ''
for sec_type, content in sections:
    if sec_type == "heading":
        level, text = content
        body_xml += build_heading(level, text)
    elif sec_type == "paragraph":
        body_xml += build_paragraph(content, size=21)
    elif sec_type == "list":
        body_xml += build_bullet_list(content)
    elif sec_type == "table":
        headers, rows = content
        body_xml += build_table(headers, rows)

# Document XML
document_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w10="urn:schemas-microsoft-com:office:word" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'mc:Ignorable="w14 wp14">'
    '<w:body>'
    f'{body_xml}'
    '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
    '</w:body>'
    '</w:document>'
)

# Styles XML with Heading styles and ListParagraph
styles_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '<w:style w:type="paragraph" w:styleId="Heading1">'
    '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="480" w:after="240"/></w:pPr>'
    '<w:rPr><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>'
    '</w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading2">'
    '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="360" w:after="200"/></w:pPr>'
    '<w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>'
    '</w:style>'
    '<w:style w:type="paragraph" w:styleId="Heading3">'
    '<w:name w:val="heading 3"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="240" w:after="160"/></w:pPr>'
    '<w:rPr><w:b/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
    '</w:style>'
    '<w:style w:type="paragraph" w:styleId="ListParagraph">'
    '<w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/>'
    '<w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>'
    '</w:style>'
    '<w:style w:type="paragraph" w:styleId="Normal" w:default="1">'
    '<w:name w:val="Normal"/>'
    '<w:pPr><w:spacing w:after="120"/><w:ind w:firstLineChars="200" w:firstLine="420"/></w:pPr>'
    '<w:rPr><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>'
    '</w:style>'
    '</w:styles>'
)

numbering_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:abstractNum w:abstractNumId="0">'
    '<w:lvl w:ilvl="0">'
    '<w:start w:val="1"/>'
    '<w:numFmt w:val="bullet"/>'
    '<w:lvlText w:val="·"/>'
    '<w:lvlJc w:val="left"/>'
    '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>'
    '</w:lvl>'
    '</w:abstractNum>'
    '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
    '</w:numbering>'
)

content_types_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
    '</Types>'
)

rels_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '</Relationships>'
)

word_rels_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
    '</Relationships>'
)

# Write the docx (ZIP file)
with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', content_types_xml)
    zf.writestr('_rels/.rels', rels_xml)
    zf.writestr('word/document.xml', document_xml)
    zf.writestr('word/styles.xml', styles_xml)
    zf.writestr('word/numbering.xml', numbering_xml)
    zf.writestr('word/_rels/document.xml.rels', word_rels_xml)

print(f"文档已生成: {OUTPUT}")
