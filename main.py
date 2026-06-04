from fastapi import FastAPI
from app.utils.json_handler import initialize_json_file

app = FastAPI(title="Quiz API",version="1.0.1")

@app.on_event("startup")
async def startup_event():
    # run when app starts : 
    initialize_json_file()
    print("App initialized !!")

@app.get("/")
async def root():
    return {"message":"Quiz API"}