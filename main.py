from fastapi import FastAPI

app = FastAPI()

tasks=[
    {"id":1,"title":"Buy Milk","done":False},
    {"id": 2, "title": "Learn FastAPI", "done": True},
    {"id": 3, "title": "Commit to GitHub", "done": False}
]
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Task API!",
        "name": "Task API", 
        "version": "1.0", 
        "endpoints": ["/tasks"] 
    }

@app.get("/health")
def read_health():
    return {
        "status": "ok"
    }

@app.get("/tasks")
def get_tasks():
    return tasks;

@app.get("/tasks/{task_id}")
def get_byid_tasks(task_id:int):
    for task in tasks:
        if(task["id"])==task_id:
            return task

        raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})
