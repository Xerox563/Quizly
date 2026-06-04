# main.py
from fastapi import FastAPI
from app.utils.json_handler import initialize_json_file
from app.routes.quizzes import router as quizzes_router

app = FastAPI(title="Quiz API", version="1.0.0")

# STARTUP
@app.on_event("startup")
async def startup_event():
    """Initialize JSON file on startup"""
    initialize_json_file()
    print("✓ App initialized")

# Include the quizzes router
# All routes from router prefixed with /quizzes
app.include_router(quizzes_router)

# ROOT ENDPOINT
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Quiz API"}