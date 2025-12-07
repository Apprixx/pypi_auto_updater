from utils.logger import log
import json
import sys
import os

DEFAULT_PACKAGE_TEMPLATE = {
    "last_checked": None,
    "last_downloaded_version": None, 
    "latest_version": None,
    "status" : None,
    "latest_releases":{}
}

def initialize_packages(input_json_path: str = "init_packages.json") -> bool:
    """
    初始化 packages.json，根据输入的JSON文件键名生成包配置
    """
    
    # 检查输出文件是否已存在
    output_path = "data/packages.json"

    # 检查输入文件是否存在
    if not os.path.isfile(input_json_path):
        log.error(f"Input JSON file not found: {input_json_path}")
        return False

    try:
        # 读取输入文件
        with open(input_json_path, "r", encoding="utf-8") as f:
            init_data = json.load(f)
        print('读取到初始化json文件【{}】共【{}】个包名称'.format(input_json_path,len(init_data)))
        # 创建包配置
        packages = {}
        for key in init_data:
            packages[key] = DEFAULT_PACKAGE_TEMPLATE.copy()
        print('根据初始json文件【{}】创建了【{}】个默认包配置'.format(input_json_path, len(packages.keys())))
        # 确保输出目录存在
        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)
        
        if os.path.isfile(output_path):
            # 如果存在输出文件，则应该进行增量更新
            with open(output_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            print('读取到运行json文件【{}】中原有【{}】个包名称'.format(output_path, len(old_data.keys())))
            # 检查所有初始化文件中的包是否都存在于old
            need_add_count = len([k for k in packages.keys() if k not in old_data.keys()])
            if need_add_count > 0:
                for key in packages.keys():
                    if key not in old_data.keys():
                        old_data[key] = packages[key]
            packages = old_data
            print('要对运行json文件【{}】追加【{}】个包名称'.format(output_path, need_add_count))
        # 写入包配置
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(packages, f, indent=2, ensure_ascii=False)
        
        log.info(f"初始化 {len(packages)} 个包到 {output_path}")
        return True
        
    except json.JSONDecodeError as e:
        log.error(f"JSON 解析失败: {e}")
        return False
    except PermissionError as e:
        log.error(f"权限被拒绝: {e}")
        return False
    except OSError as e:
        log.error(f"OS 错误: {e}")
        return False
    except Exception as e:
        log.error(f"未知错误: {e}")
        return False
    