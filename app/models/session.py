from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from ..db import Base


class FitSession(Base):
    __tablename__ = "fit_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    video_path = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
