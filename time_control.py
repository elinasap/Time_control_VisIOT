import subprocess
import sys

scripts = ["sbscr.py", "web_server.py"]

processes = []
for script in scripts:
    process = subprocess.Popen([sys.executable, script])
    processes.append(process)

# Дождаться завершения всех процессов (опционально)
for process in processes:
    process.wait()