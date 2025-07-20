setlocal

IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate

pip install -r requirements.txt

if "%1"=="--build" (
    pyinstaller --onefile desktop.py --noconsole --name "Financieel Overzicht"
)

python desktop.py --debug
