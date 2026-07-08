from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Date, DateTime
from datetime import date, datetime
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    todo_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Todo(id={self.id}, title={self.title}, done={self.done}, todo_date={self.todo_date}, created_at={self.created_at})>"