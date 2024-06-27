from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import Integer, String, Float, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column
db = SQLAlchemy()


class RecordsModel(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date = mapped_column(Date)
    is_expense: Mapped[bool] = mapped_column(Boolean)
    amount: Mapped[float] = mapped_column(Float)
    reporter: Mapped[str] = mapped_column(String)
    tag: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
