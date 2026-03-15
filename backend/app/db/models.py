from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean

from app.db.session import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    function_id = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    admin_token = Column(String, nullable=False)
    status = Column(String, default="running", nullable=False)
    max_steps = Column(Integer, nullable=False, default=30)
    participants = relationship("ParticipantModel", back_populates="session", cascade="all, delete-orphan")


class ParticipantModel(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    participant_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    found_step = Column(Integer, nullable=True)
    found_z = Column(Float, nullable=True)
    is_bot = Column(Boolean, nullable=False, default=False)

    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("SessionModel", back_populates="participants")

    clicks = relationship("ClickModel", back_populates="participant", cascade="all, delete-orphan")


class ClickModel(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    step = Column(Integer, nullable=False)

    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    participant = relationship("ParticipantModel", back_populates="clicks")