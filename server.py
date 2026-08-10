from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# 1. Раздаём файлы из папки webapp
if os.path.exists("webapp"):
    app.mount("/static", StaticFiles(directory="webapp"), name="static")

# 2. Ищем index.html и в webapp/, и в корне (на всякий случай)
@app.get("/")
async def read_root():
    if os.path.exists("webapp/index.html"):
        return FileResponse("webapp/index.html")
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html netu naxui"}
