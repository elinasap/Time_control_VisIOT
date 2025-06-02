import subprocess
import sys
import webbrowser
scripts = ["sbscr.py", "web_server.py"]

processes = []
for script in scripts:
    process = subprocess.Popen([sys.executable, script])
    processes.append(process)

webbrowser.open("http://localhost:5000/")

# Дождаться завершения всех процессов (опционально)
for process in processes:
    process.wait()