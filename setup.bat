setlocal

IF NOT EXIST venv (
    python -m venv venv
)
call venv\Scripts\activate

pip install -r requirements.txt

python desktop.py
