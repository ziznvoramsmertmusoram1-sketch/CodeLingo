from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Раздаём css и js из папки webapp по пути /webapp
if os.path.exists("webapp"):
    app.mount("/webapp", StaticFiles(directory="webapp"), name="webapp")

# Главная страница отдаёт index.html из корня
@app.get("/")
async def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html not found"}
