from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.db import Base


class Bike(Base):
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String)
    weight_kg = Column(Float)

    stack = Column(Float)
    reach = Column(Float)
    top_tube_length = Column(Float)
    seat_tube_angle = Column(Float)
    head_tube_angle = Column(Float)
    seat_height = Column(Float)
    saddle_setback = Column(Float)
    stem_length = Column(Float)
    handlebar_width = Column(Float)
    crank_length = Column(Float)
