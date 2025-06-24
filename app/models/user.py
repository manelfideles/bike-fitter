from sqlalchemy import Column, Float, Integer, String

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=True)
    inseam_cm = Column(Float)
    torso_cm = Column(Float)
    arm_cm = Column(Float)
    shoulder_cm = Column(Float)
    riding_position = Column(String)  # 'aero', 'sport', 'comfort'
