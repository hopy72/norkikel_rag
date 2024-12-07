import uvicorn
from fastapi import FastAPI
from src.routers.search_router import search_router

app = FastAPI(title="Document Search Service")

# Подключение роутеров
app.include_router(search_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
