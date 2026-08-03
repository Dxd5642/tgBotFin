from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    username: Mapped[str]
    name: Mapped[Optional[str]]
    second_name: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    actions: Mapped[List["Actions"]] = relationship(back_populates="user")
    mountlysummary: Mapped[List["MountlySummary"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<Users(chat_id={self.chat_id}, username={self.username}, name={self.name}, second_name={self.second_name}, created_at={self.created_at})>"


class Checks(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float]
    desc: Mapped[str] = mapped_column(default="Прочие доходы")
 

class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]



class Actions(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"))
    check_id: Mapped[int] = mapped_column(ForeignKey("checks.id"))
    date: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["Users"] = relationship(back_populates="actions")
    status: Mapped["Status"] = relationship()
    check: Mapped["Checks"] = relationship()


class MountlySummary(Base): # С каждым сообщением пользователя проверяем есть ли запись на месяц
    __tablename__ = "mountlysummary"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id"))
    year: Mapped[int]
    month: Mapped[int]
    total_income: Mapped[float] = mapped_column(default=0.0)
    total_expense: Mapped[float] = mapped_column(default=0.0)
    start_balance: Mapped[float]
    end_balance: Mapped[float]

    user: Mapped["Users"] = relationship(back_populates="mountlysummary")

