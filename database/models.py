from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Farm(Base):
    __tablename__ = "farms"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(255),
        nullable=True
    )

    area = Column(
        String(50),
        nullable=True
    )

    palms = Column(
        String(50),
        nullable=True
    )

    plantation_type = Column(
        String(100),
        nullable=True
    )

    water_source = Column(
        String(100),
        nullable=True
    )

    irrigation = Column(
        String(100),
        nullable=True
    )

    soil = Column(
        String(100),
        nullable=True
    )

    plantation_date = Column(
        String(50),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )