setlocal

IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate

pip install -r requirements.txt

if "%1"=="--build" (
    pip install pyinstaller

    pyinstaller --onefile --noconsole --name LesInkomstenApp --icon=app_icon.ico main.py
)

if "%1"=="--run" (
    python main.py --debug
)
