from fastapi import FastAPI

app = FastAPI(
    title = "TaskFlow API",
    description = "A task management application built with Python",
    version = "0.1.0"
)

@app.get("/")

def home():
    return {
        "message" : "Welcome to TaskFlow API", 
        "status" : "running"
    }

@app.get("/health")

def health_check():
    return{
        "status" : "healthy"
    }