from fastapi import FastAPI
from database import engine
import models

from routers import users, wallets

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wallet System API")

app.include_router(users.router)
app.include_router(wallets.router)

@app.get("/")
async def read_root(): 
    return {"message": "готово к работе"}
