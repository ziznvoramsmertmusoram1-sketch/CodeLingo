from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def read_root():
    root_files = os.listdir(".")
    webapp_files = os.listdir("webapp") if os.path.exists("webapp") else "Папки webapp нет"
    return {
        "текущая_папка": os.getcwd(),
        "файлы_в_корне": root_files,
        "файлы_в_webapp": webapp_files
    }
