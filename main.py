import os
from core.package_manager import run_package_workflow 
from utils.archive_generator import main as archive_generator
from utils.remove_empty_folders import remove_empty_folders_simple
from config import check_config

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    check_config()
    run_package_workflow()
    remove_empty_folders_simple()
    archive_generator()


