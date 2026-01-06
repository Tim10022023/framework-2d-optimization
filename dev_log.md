
## venv aktivieren

backend\.venv\Scripts\activate
oder 
.\backend\.venv\Scripts\Activate.ps1


## backend starten
cd backend

pip install -r requirements.txt

uvicorn app.main:app --reload
