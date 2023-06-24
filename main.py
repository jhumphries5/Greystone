import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import create_tables
from routers import routers

app = FastAPI(
    title="Lending API",
    description="API for managing loans",
    version="0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

[app.include_router(router) for router in routers]

# Run the API
if __name__ == "__main__":
    create_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)