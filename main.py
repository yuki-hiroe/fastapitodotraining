from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from database import SessionLocal, engine, Base
from typing import Generator
from sqlalchemy.orm import Session
from models import Todo

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

# テンプレートディレクトリを指定
templates = Jinja2Templates(directory="templates")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    todos = db.query(Todo).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "title": "Todo List", "todos": todos})

@app.get("/about/{todo_id}", response_class=HTMLResponse)
def read_about(request: Request, todo_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    todo = next((todo for todo in db.query(Todo).all() if todo.id == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return templates.TemplateResponse(request=request, name="about.html", context={"request": request, "title": "About Page", "todo": todo})

@app.post("/add", response_class=HTMLResponse)
def add_todo(_request: Request, title: str = Form(...), db: Session = Depends(get_db)) -> RedirectResponse:
    todo = Todo(title=title, done=False)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{todo_id}", response_class=HTMLResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/done/{todo_id}", response_class=HTMLResponse)
def done_todo(todo_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return RedirectResponse(url="/", status_code=303)