REM check if venv exists, create if not
IF NOT EXIST "venv" (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
)

REM Open default browser with specified URL
start "" http:127.0.0.1:5000

REM run application
python main.py

