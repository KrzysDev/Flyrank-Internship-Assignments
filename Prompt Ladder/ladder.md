# Prompt Ladder – FastAPI Todo CRUD API

---

## Baseline

**Prompt:**
```
make a CRUD api in fastapi python for a todolist
```

**Response:**

Here's a clean, production-friendly CRUD API for a Todo List using **FastAPI**, **SQLAlchemy**, and **SQLite**.

### Project Structure
```text
todo-api/
│── main.py
│── database.py
│── models.py
│── schemas.py
│── crud.py
│── requirements.txt
```

**`database.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`models.py`**
```python
from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
```

**`schemas.py`**
```python
from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool

    model_config = {
        "from_attributes": True
    }
```

**`crud.py`**
```python
from sqlalchemy.orm import Session
import models
import schemas


def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_todos(db: Session):
    return db.query(models.Todo).all()


def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = get_todo(db, todo_id)

    if not db_todo:
        return None

    updates = todo.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)

    return db_todo


def delete_todo(db: Session, todo_id: int):
    db_todo = get_todo(db, todo_id)

    if not db_todo:
        return None

    db.delete(db_todo)
    db.commit()

    return db_todo
```

**`main.py`**
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
import crud

from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API")


@app.get("/")
def home():
    return {"message": "Todo API is running"}


@app.post("/todos", response_model=schemas.TodoResponse)
def create(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)


@app.get("/todos", response_model=list[schemas.TodoResponse])
def read_all(db: Session = Depends(get_db)):
    return crud.get_todos(db)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def read_one(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, todo_id)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    updated = crud.update_todo(db, todo_id, todo)

    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")

    return updated


@app.delete("/todos/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_todo(db, todo_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "Todo deleted successfully"}
```

**Endpoint table, run instructions, and example request/response** were also included (health check `/`, full CRUD on `/todos`, Swagger/ReDoc links, example JSON for create).

**Notes:**
This is the baseline — no single change to describe, since nothing has been engineered yet.
---

## Version 1 — Layer: **Constraints**

**Prompt:**
```
Build a small CRUD API for a todo list using Python and FastAPI.
Requirements:
- No database, store everything in memory (a Python list)
- Endpoints: /tasks with GET, POST, PUT, DELETE
```

**Response:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Todo CRUD API")


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    completed: bool


# In-memory storage
tasks: List[Task] = []
next_id = 1


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    global next_id

    new_task = Task(
        id=next_id,
        title=task.title,
        completed=False,
    )

    tasks.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated: TaskUpdate):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks[index] = Task(
                id=task_id,
                title=updated.title,
                completed=updated.completed,
            )
            return tasks[index]

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[index]
            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")
```

**Notes:**
- **What changed in the prompt:** Added a hard constraint (no database, store in a Python list) and pinned down the exact endpoint contract (`/tasks`, GET/POST/PUT/DELETE).
- **What actually improved in the output:** The model stopped inventing infrastructure nobody asked for — SQLAlchemy, SQLite, and the 5-file split all disappeared. The whole thing collapsed to one ~50-line file that does exactly what was asked, nothing more.
- **What still failed:** Zero comments or explanation of any FastAPI-specific mechanism, so it's not usable as a learning artifact. No input validation beyond basic types (an empty-string title is accepted). `next_id` is a bare global variable, which works but is a fragile pattern going forward.
- **What I'd try next:** Since correctness is solid but the code is dense and unexplained, the next layer to test is whether specifying an audience makes it more approachable — and whether that comes at any cost.

---

## Version 2 — Layer: **Audience**

**Prompt:**
```
Build a small CRUD API for a todo list using Python and FastAPI.
Requirements:
- No database, store everything in memory (a Python list)
- Endpoints: /tasks with GET, POST, PUT, DELETE
Write this for a junior developer who has never used FastAPI before —
add short comments explaining what each FastAPI-specific piece does
(Depends, response_model, pydantic BaseModel).
```

**Response:**
```python
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

# Create the FastAPI application
app = FastAPI()


# BaseModel comes from Pydantic.
# It validates incoming JSON and converts it into a Python object.
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


# This list acts as our "database".
# Everything is stored in memory, so data disappears when the server stops.
tasks: List[Task] = []


# Depends tells FastAPI to call this function automatically
# and pass its return value into the endpoint.
# Here we use it to find a task by its ID.
def get_task(task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/tasks", response_model=List[Task])
# response_model tells FastAPI what the response should look like.
# It validates the output and automatically creates API documentation.
def list_tasks():
    return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    # Prevent duplicate IDs.
    if any(existing.id == task.id for existing in tasks):
        raise HTTPException(status_code=400, detail="Task ID already exists")

    tasks.append(task)
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(updated_task: Task, task: Task = Depends(get_task)):
    # 'task' is automatically provided by Depends(get_task).
    # If the task doesn't exist, get_task raises a 404 error.
    task.title = updated_task.title
    task.completed = updated_task.completed
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task: Task = Depends(get_task)):
    tasks.remove(task)
    return {"message": "Task deleted"}
```

**Notes:**
- **What changed in the prompt:** Added an audience specification (junior developer new to FastAPI) plus an explicit instruction to comment on named FastAPI mechanisms: `Depends`, `response_model`, `BaseModel`.
- **What actually improved in the output:** Real, targeted comments appeared exactly where requested — right above `BaseModel`, `response_model`, and `Depends` — and they're accurate, not filler. This is the first version that could double as a teaching artifact.
- **What still failed / this made it worse:** To showcase `Depends`, the model restructured `create_task` to take a full `Task` (including `id`) instead of the `TaskCreate`/auto-increment pattern from Version 1. Now the *client* has to invent a unique ID and the server merely rejects duplicates — a straight regression in API design versus Version 1, introduced purely as a side effect of writing a teaching example. **This is the honest "made it worse" moment**: making the code more explainable pushed it toward a worse contract.
- **What I'd try next:** Keep the comment style, but explicitly re-state the auto-increment ID constraint in the next version so the audience layer doesn't silently override earlier decisions again.

---

## Version 3 — Layer: **Output format**

**Prompt:**
```
Build a small CRUD API for a todo list using Python and FastAPI.
Requirements:
- No database, store everything in memory (a Python list)
- Endpoints: /tasks with GET, POST, PUT, DELETE
Write this for a junior developer who has never used FastAPI before —
add short comments explaining what each FastAPI-specific piece does
(Depends, response_model, pydantic BaseModel).
Return the answer as:
1. A single main.py file (no multi-file split)
2. A table of all endpoints (method, path, description)
3. Three example curl commands
```

**Response:**

**1. `main.py`**
```python
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Simple Todo API")

# This is our "database".
# Everything is stored in this Python list while the app is running.
tasks = []


# BaseModel (from Pydantic)
# -------------------------
# BaseModel defines the shape of the data FastAPI expects.
# It also validates incoming JSON automatically.
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


# This model is used when creating a new task.
# The client does not need to send an id.
class TaskCreate(BaseModel):
    title: str


# This model is used when updating a task.
# Optional means the client can update only the fields they want.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


# Depends(...)
# ------------
# Depends lets FastAPI automatically call a function before your endpoint.
# It is commonly used for authentication, database connections, or shared logic.
# Here we use it simply to demonstrate how dependency injection works.
def get_tasks():
    return tasks


@app.get("/tasks", response_model=List[Task])
def get_all_tasks(task_list=Depends(get_tasks)):
    # response_model tells FastAPI what the response should look like.
    # It validates the output and automatically generates API documentation.
    return task_list


@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate, task_list=Depends(get_tasks)):
    new_task = Task(
        id=len(task_list) + 1,
        title=task.title,
        completed=False,
    )

    task_list.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, update: TaskUpdate, task_list=Depends(get_tasks)):
    for task in task_list:
        if task.id == task_id:
            if update.title is not None:
                task.title = update.title

            if update.completed is not None:
                task.completed = update.completed

            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, task_list=Depends(get_tasks)):
    for index, task in enumerate(task_list):
        if task.id == task_id:
            task_list.pop(index)
            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")
```

**2. Endpoint Table**

| Method | Path               | Description             |
| ------ | ------------------ | ------------------------ |
| GET    | `/tasks`           | Return all tasks         |
| POST   | `/tasks`           | Create a new task        |
| PUT    | `/tasks/{task_id}` | Update an existing task  |
| DELETE | `/tasks/{task_id}` | Delete a task by its ID  |

**3. Example curl commands**
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI"}'

curl http://127.0.0.1:8000/tasks

curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Notes:**
- **What changed in the prompt:** Added an explicit output format contract — one file, an endpoint table, and three curl examples.
- **What actually improved in the output:** The response is now scannable and directly actionable — the table lets you check the API surface at a glance without reading code, and the curl commands are copy-pasteable and correct. It also incidentally fixed Version 2's regression: `TaskCreate` (no `id` field) came back, restoring server-side ID assignment.
- **What still failed:** `id=len(task_list) + 1` is a new, worse bug — after any deletion, `len(task_list) + 1` will collide with an existing ID (e.g. create 3 tasks, delete task 2, create a new one → ID collision with task 3). This wasn't a problem in Version 1 (proper counter) but reappeared here because ID logic wasn't pinned down as a constraint in this prompt.
- **What I'd try next:** Explicitly state quality requirements — correct status codes, validation, and no ID collisions — since format constraints alone don't protect logic that isn't restated every round.

---

## Version 4 — Layer: **Quality criteria**

**Prompt:**
```
Build a small CRUD API for a todo list using Python and FastAPI.
Requirements:
- No database, store everything in memory (a Python list)
- Endpoints: /tasks with GET, POST, PUT, DELETE
Write this for a junior developer who has never used FastAPI before —
add short comments explaining what each FastAPI-specific piece does
(Depends, response_model, pydantic BaseModel).
Return the answer as:
1. A single main.py file (no multi-file split)
2. A table of all endpoints (method, path, description)
3. Three example curl commands
The code must satisfy:
- Proper HTTP status codes (201 for created, 404 for not found, 204 for deleted)
- Input validation with Pydantic (title required, non-empty)
- No global mutable state bugs (e.g. next_id must not collide after deletions)
```

**Response:**

**1. `main.py`**
```python
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Simple Todo API")


class TaskStore:
    """
    Holds all tasks in memory.
    next_id is only increased, never decreased.
    This avoids ID collisions after deleting tasks.
    """
    def __init__(self):
        self.tasks = []
        self.next_id = 1


store = TaskStore()


def get_store() -> TaskStore:
    return store


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title")
    completed: bool = False


class Task(BaseModel):
    id: int
    title: str
    completed: bool


@app.get("/tasks", response_model=List[Task])
def get_tasks(store: TaskStore = Depends(get_store)):
    return store.tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, store: TaskStore = Depends(get_store)):
    new_task = Task(id=store.next_id, title=task.title, completed=task.completed)
    store.tasks.append(new_task)
    store.next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate, store: TaskStore = Depends(get_store)):
    for index, existing in enumerate(store.tasks):
        if existing.id == task_id:
            updated = Task(id=task_id, title=task.title, completed=task.completed)
            store.tasks[index] = updated
            return updated

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, store: TaskStore = Depends(get_store)):
    for index, task in enumerate(store.tasks):
        if task.id == task_id:
            del store.tasks[index]
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
```

**2. Endpoint table** and **3. curl examples** were also returned (create/list/delete), consistent with Version 3's format.

**Notes:**
- **What changed in the prompt:** Added three concrete quality requirements — correct status codes, non-empty title validation, and no ID collisions after deletion.
- **What actually improved in the output:** The ID bug from Version 3 is gone — IDs now come from a counter wrapped in a `TaskStore` class rather than `len(list) + 1`, so deletions no longer cause collisions. Status codes are now explicit and correct (201/204/404) instead of FastAPI's defaults. `Field(..., min_length=1)` actually rejects empty titles now, which is a real, testable behavior change (not just a comment).
- **What still failed:** The self-imposed "junior dev" comments got noticeably thinner in this version — the docstring on `TaskStore` survived, but the per-endpoint explanations of `response_model` and `Depends` from Version 2/3 are gone. Adding a quality-criteria layer quietly cost some of the audience layer's gains; nothing in the prompt asked to drop those comments back down.
- **What I'd try next:** Add an explicit review/verification instruction so the model actively checks its own output against the stated failure modes, rather than relying on hoping the constraints stick across rounds.

---

## Version 5 — Layer: **Review / verification instructions**

**Prompt:**
```
Build a small CRUD API for a todo list using Python and FastAPI.
Requirements:
- No database, store everything in memory (a Python list)
- Endpoints: /tasks with GET, POST, PUT, DELETE
Write this for a junior developer who has never used FastAPI before —
add short comments explaining what each FastAPI-specific piece does
(Depends, response_model, pydantic BaseModel).
Return the answer as:
1. A single main.py file (no multi-file split)
2. A table of all endpoints (method, path, description)
3. Three example curl commands
The code must satisfy:
- Proper HTTP status codes (201 for created, 404 for not found, 204 for deleted)
- Input validation with Pydantic (title required, non-empty)
- No global mutable state bugs (e.g. next_id must not collide after deletions)

Before giving the final answer, check your own code for these failure modes
and fix them if present: duplicate IDs after several deletes, missing
docs for query parameters, and any endpoint that doesn't return a
proper response_model. List the checks you did at the end of your answer.
```

**Response:**

**1. `main.py`**
```python
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="In-Memory Todo API")


# BaseModel tells FastAPI how to:
# - validate incoming JSON
# - convert Python objects to JSON
# - generate API documentation automatically
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title (must not be empty).")
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, description="Updated task title (must not be empty).")
    completed: bool


class Task(BaseModel):
    id: int
    title: str
    completed: bool


tasks: List[Task] = []

# This always increases and is never reused.
# That prevents duplicate IDs after deletions.
next_id = 1


# Depends tells FastAPI to call this function automatically
# before the endpoint runs. It's useful for shared logic like
# authentication, database connections, or configuration.
def get_tasks() -> List[Task]:
    return tasks


@app.get("/tasks", response_model=List[Task])
def list_tasks(
    completed: Optional[bool] = Query(
        default=None,
        description="Optional filter by completion status.",
    ),
    task_list: List[Task] = Depends(get_tasks),
):
    if completed is None:
        return task_list
    return [task for task in task_list if task.completed == completed]


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, task_list: List[Task] = Depends(get_tasks)):
    global next_id
    new_task = Task(id=next_id, title=task.title, completed=task.completed)
    task_list.append(new_task)
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated: TaskUpdate, task_list: List[Task] = Depends(get_tasks)):
    for index, task in enumerate(task_list):
        if task.id == task_id:
            new_task = Task(id=task.id, title=updated.title, completed=updated.completed)
            task_list[index] = new_task
            return new_task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, task_list: List[Task] = Depends(get_tasks)):
    for index, task in enumerate(task_list):
        if task.id == task_id:
            task_list.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
```

**2. Endpoint table** (now documents the new `completed` query parameter on GET) and **3. curl examples** were included.

**Self-checks performed (as returned by the model):**
- ✅ Duplicate IDs after deletions: `next_id` is monotonically increasing, never reused.
- ✅ Missing docs for query parameters: `completed` uses `Query(..., description=...)`.
- ✅ Missing `response_model`: all body-returning endpoints have one; DELETE correctly omits it since it returns 204.

**Notes:**
- **What changed in the prompt:** Added an explicit self-review instruction naming three specific failure modes to check for, plus a requirement to report which checks were performed.
- **What actually improved in the output:** A genuinely new feature appeared unprompted — a `completed` query filter on GET `/tasks` — which the model then correctly flagged and documented as part of satisfying "missing docs for query parameters." The self-check list at the end is specific and maps 1:1 to the requested failure modes, not generic reassurance.
- **What still failed:** The verification is self-reported, not independently proven — the model asserts "IDs cannot collide" but doesn't demonstrate it against a test case (e.g. create 3, delete 1, create again). There's no way to know from the output alone whether the check was real reasoning or a plausible-sounding checklist generated after the fact.
- **What I'd try next:** For a stranger to trust this, the next real upgrade would be asking for an actual test case or example walkthrough (e.g. "trace through create→delete→create and show the resulting IDs") rather than a self-attested checklist — that would turn "I checked" into something verifiable in the output itself.

---

## Final Reusable Prompt

```
Build a small CRUD API for a todo list using Python and FastAPI.

Requirements:
- No database — store everything in memory using a Python list, wrapped
  in a simple class (avoid raw global variables)
- Endpoints: /tasks with GET, POST, PUT, DELETE
- Task IDs are auto-generated by the server (never accepted from the client)
  and must never collide, even after deletions

Audience: a junior developer new to FastAPI. Add short inline comments
explaining FastAPI-specific mechanisms (Depends, response_model, Pydantic
BaseModel) — but keep comments concise, don't over-explain basic Python.

Output format:
1. A single main.py file
2. A table of all endpoints (method, path, description)
3. Three example curl commands

Quality requirements:
- Correct HTTP status codes (201 created, 404 not found, 204 deleted)
- Pydantic validation: title is required and non-empty
- No ID collisions after deletions

Before your final answer, trace through a concrete scenario (create 3 tasks,
delete the 2nd, create a 4th) and confirm the resulting IDs don't collide.
Also verify: no endpoint is missing a response_model, and any query
parameters are documented. List the checks you performed at the end.
```

This folds in every layer that held up (constraints, format, quality criteria, verification) and repairs the two regressions found along the way: the client-supplied-ID problem from Version 2, and the unverifiable self-check from Version 5, replaced with a concrete trace-through requirement.