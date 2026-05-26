import os
import subprocess
import sys
from config import START_TIME


def create_daily_task(task_name="PyPI_Auto_Updater", start_time=START_TIME):
    """
    创建一个 Windows 计划任务：
    每天在指定时间运行当前目录下的 main.py。
    如果存在同名任务，则删除旧任务。
    """

    # 当前目录与 main.py 路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_py):
        print(f"❌ 错误：未找到 main.py ({main_py})")
        return

    # 检查是否已有旧任务
    print(f"🔍 检查是否已有任务 '{task_name}' ...")
    query_cmd = ["schtasks", "/query", "/tn", task_name]
    exists = subprocess.run(query_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

    if exists:
        print("⚠️ 发现旧任务，正在删除...")
        subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL)

    # 构造计划任务命令
    python_exec = sys.executable or "python"
    # 使用 cmd /c 切换到目录再运行 main.py
    cmd_line = f'cmd /c "cd /d {script_dir} && {python_exec} main.py"'

    print(f"🕒 正在创建计划任务，每天 {start_time} 执行 main.py ...")
    result = subprocess.run([
        "schtasks",
        "/create",
        "/tn", task_name,
        "/tr", cmd_line,
        "/sc", "daily",
        "/st", start_time,
        "/f"
    ])

    if result.returncode == 0:
        print(f"✅ 已成功创建计划任务 '{task_name}'")
        print(f"🕒 计划任务将在每天 {start_time} 运行：{main_py}")
        print(f"▶ 可立即执行：schtasks /run /tn \"{task_name}\"")
    else:
        print("❌ 创建计划任务失败")

if __name__ == "__main__":
    create_daily_task()
