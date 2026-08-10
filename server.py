from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Отдаём главную страницу index.html из папки webapp
@app.get("/")
async def read_root():
    return FileResponse("webapp/index.html")

# Подключаем остальные статические файлы (style.css, app.js)
if os.path.exists("webapp"):
    app.mount("/", StaticFiles(directory="webapp"), name="static")

