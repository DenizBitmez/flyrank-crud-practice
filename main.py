from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import sqlite3
app = FastAPI()

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy milk", 0),
                ("Learn FastAPI & SQLite", 0),
                ("Build a persistent CRUD API", 0)
            ]
        )
        conn.commit()
    
    conn.close()

init_db()

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
    conn=sqlite3.connect("tasks.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows=cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get tasks by id")
def get_task(id:int):
    conn=sqlite3.connect("tasks.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?")
    row=cursor.fetchall()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    return dict(row)


class TaskCreate(BaseModel):
    title:str


@app.post("/tasks",status_code=201,summary="Create tasks")
def create_task(task_data: TaskCreate):
    if not task_data.title or task_data.title.strip() == "":
        raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task_data.title.strip(), 0)
    )
    conn.commit()
    
    new_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    new_task = dict(cursor.fetchone())
    conn.close()
    
    return new_task

class TaskUpdate(BaseModel):
    title:str | None=None
    done:bool | None=None

@app.put("/tasks/{task_id}",summary="Update tasks")
def update_task(id:int, task_data:TaskUpdate):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    
    new_title = task["title"]
    new_done = task["done"]
    
    if task_data.title is not None:
        if task_data.title.strip() == "":
            conn.close()
            raise HTTPException(status_code=400, detail={"error": "Title cannot be empty"})
        new_title = task_data.title.strip()
        
    if task_data.done is not None:
        new_done = 1 if task_data.done else 0
        
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, id)
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    updated_task = dict(cursor.fetchone())
    conn.close()
    return updated_task

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete tasks")
def delete_task(id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail={"error": "Task not found"})
    
    # Veritabanından sil
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return

@app.get("/stats")
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    done_count = cursor.fetchone()[0]
    
    open_count = total - done_count
    conn.close()
    
    return {"total": total, "done": done_count, "open": open_count}