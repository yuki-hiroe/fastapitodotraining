from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # title と done を追加してみてください
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(Boolean, default=False)