import os
from core.package_manager import run_package_workflow 
from utils.archive_generator import main as archive_generator
from utils.remove_empty_folders import remove_empty_folders_simple
from config import check_config

from defender_update import main as def_main

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    check_config()
    run_package_workflow()
    remove_empty_folders_simple()
    archive_generator()
    # 开始下载微软病毒库    
    def_main()
# import json
# from collections import Counter

# with open('packages.json', 'r', encoding='utf-8') as f:
#      packages_data = json.load(f)

# Counter([p['status'] for p in packages_data.values()])

