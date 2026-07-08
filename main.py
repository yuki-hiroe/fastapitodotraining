from fastapi import FastAPI, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from database import SessionLocal, engine, Base
from typing import Generator
from sqlalchemy.orm import Session
from datetime import date
import calendar
from models import Todo

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

# テンプレートディレクトリを指定
templates = Jinja2Templates(directory="templates")

WEEKDAY_LABELS = ["月", "火", "水", "木", "金", "土", "日"]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_calendar_weeks(
    cal_year: int,
    cal_month: int,
    dates_with_todos: set[date],
    selected_date: date | None = None,
) -> list[list[dict | None]]:
    today = date.today()
    weeks: list[list[dict | None]] = []

    for week in calendar.monthcalendar(cal_year, cal_month):
        week_days: list[dict | None] = []
        for day in week:
            if day == 0:
                week_days.append(None)
                continue
            current = date(cal_year, cal_month, day)
            week_days.append(
                {
                    "day": day,
                    "iso": current.isoformat(),
                    "is_selected": selected_date is not None and current == selected_date,
                    "is_today": current == today,
                    "has_todos": current in dates_with_todos,
                }
            )
        weeks.append(week_days)

    return weeks


def get_month_bounds(cal_year: int, cal_month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(cal_year, cal_month)[1]
    return date(cal_year, cal_month, 1), date(cal_year, cal_month, last_day)


def shift_month(cal_year: int, cal_month: int, delta: int) -> tuple[int, int]:
    cal_month += delta
    while cal_month < 1:
        cal_month += 12
        cal_year -= 1
    while cal_month > 12:
        cal_month -= 12
        cal_year += 1
    return cal_year, cal_month


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    cal_year: int | None = Query(default=None),
    cal_month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    today = date.today()

    if cal_year is None:
        cal_year = today.year
    if cal_month is None:
        cal_month = today.month

    month_start, month_end = get_month_bounds(cal_year, cal_month)
    todo_dates = {
        row[0]
        for row in db.query(Todo.todo_date)
        .filter(Todo.todo_date >= month_start, Todo.todo_date <= month_end)
        .distinct()
        .all()
    }

    prev_year, prev_month = shift_month(cal_year, cal_month, -1)
    next_year, next_month = shift_month(cal_year, cal_month, 1)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "title": "カレンダー",
            "cal_year": cal_year,
            "cal_month": cal_month,
            "cal_title": f"{cal_year}年{cal_month}月",
            "weekday_labels": WEEKDAY_LABELS,
            "calendar_weeks": build_calendar_weeks(
                cal_year, cal_month, todo_dates
            ),
            "prev_cal_year": prev_year,
            "prev_cal_month": prev_month,
            "next_cal_year": next_year,
            "next_cal_month": next_month,
        },
    )


@app.get("/todos/{selected_date}", response_class=HTMLResponse)
def read_todos(
    request: Request,
    selected_date: date,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    todos = db.query(Todo).filter(Todo.todo_date == selected_date).all()
    return templates.TemplateResponse(
        request=request,
        name="todo.html",
        context={
            "request": request,
            "title": "Todo List",
            "todos": todos,
            "selected_date": selected_date,
        },
    )

@app.get("/about/{todo_id}", response_class=HTMLResponse)
def read_about(request: Request, todo_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    todo = next((todo for todo in db.query(Todo).all() if todo.id == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return templates.TemplateResponse(request=request, name="about.html", context={"request": request, "title": "About Page", "todo": todo})

@app.post("/add", response_class=HTMLResponse)
def add_todo(_request: Request, title: str = Form(...), todo_date: date = Form(...), db: Session = Depends(get_db)) -> RedirectResponse:
    todo = Todo(title=title, done=False, todo_date=todo_date)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return RedirectResponse(url=f"/todos/{todo_date}", status_code=303)

@app.post("/delete/{todo_id}", response_class=HTMLResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=f"/todos/{todo.todo_date}", status_code=303)

@app.post("/done/{todo_id}", response_class=HTMLResponse)
def done_todo(todo_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.done = not todo.done
    db.commit()
    db.refresh(todo)
    return RedirectResponse(url=f"/todos/{todo.todo_date}", status_code=303)