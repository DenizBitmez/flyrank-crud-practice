from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
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

@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    return tasks;

@app.get("/tasks/{task_id}", summary="Get tasks by id")
def get_task(task_id:int):
    for task in tasks:
        if(task["id"])==task_id:
            return task

        raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})


class TaskCreate(BaseModel):
    title:str


@app.post("/tasks",status_code=201,summary="Create tasks")
def create_task(taskData:TaskCreate):
    if not taskData.title or taskData.title.strip() == "":
        raise HTTPException(status_code=400, detail={"error": "Title is required"})

    new_id=tasks[-1]["id"] +1 if tasks else 1

    new_task= {
        "id":new_id,
        "title":taskData.title,
        "done":False
    }

    tasks.append(new_task)
    return new_task

class TaskUpdate(BaseModel):
    title:str | None=None
    done:bool | None=None

@app.put("/tasks/{task_id}",summary="Update tasks")
def update_task(task_id:int, task_data:TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if task_data.title is not None:
                if task_data.title.strip() == "":
                    raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
                task["title"] = task_data.title
            if task_data.done is not None:
                task["done"] = task_data.done

            return task

    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete tasks")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return 

    raise HTTPException(status_code=404, detail={"error": f"Task {task_id} not found"})