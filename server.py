from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Сначала раздаём статические файлы из папки webapp по пути /webapp
if os.path.exists("webapp"):
    app.mount("/webapp", StaticFiles(directory="webapp"), name="webapp")

# Главная страница корректно отдаёт index.html
@app.get("/")
async def read_root():
    index_path = os.path.join("webapp", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found in webapp folder"}


