from sqlalchemy import Column, Float, ForeignKey, Integer

from ..db import Base


class JointMeasurement(Base):
    __tablename__ = "joint_measurements"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("fit_sessions.id"), nullable=False)
    frame_number = Column(Integer)
    knee_angle = Column(Float)
    hip_angle = Column(Float)
    torso_angle = Column(Float)
    arm_angle = Column(Float)
