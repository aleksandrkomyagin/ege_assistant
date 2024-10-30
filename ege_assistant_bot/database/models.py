from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, String, Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Student(Base):

    __tablename__ = "student"
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    scores: Mapped[List["StudentScore"]] = relationship(
        "StudentScore",
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Subject(Base):

    __tablename__ = "subject"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    scores: Mapped[List["StudentScore"]] = relationship(back_populates="subject")


class StudentScore(Base):

    __tablename__ = "student_score"
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"), nullable=False)
    student: Mapped["Student"] = relationship("Student", back_populates="scores", lazy="joined")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="scores", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "subject_id",
            name="_student_subject_uc"
        ),
    )

