import locale
import webview
import subprocess
import time
import sys
import os

def main():
    if os.environ.get("STREAMLIT_STARTED") == "1":
        return

    env = os.environ.copy()
    env["STREAMLIT_STARTED"] = "1"
    
    try:
        locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")
    except locale.Error:
        pass

    debug_mode = "--debug" in sys.argv or os.environ.get("DEBUG") == "1"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/app.py",
            "--browser.serverAddress=localhost",
            "--server.headless=true",
            *(['--client.toolbarMode=none'] if not debug_mode else []),
            "--server.port=8501",
            "--server.enableCORS=false",
        ],
        env=env,
    )

    time.sleep(3) 

    webview.create_window("Financieel Overzicht", "http://localhost:8501")
    webview.start()

    proc.terminate()
    proc.wait()

if __name__ == "__main__":
    main()
