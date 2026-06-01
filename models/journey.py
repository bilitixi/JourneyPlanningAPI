from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base


class Journey(Base):
    __tablename__ = 'journeys'

    journey_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Numeric(10, 2), nullable=False)
    people = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship with User
    user = relationship("User", back_populates="journeys")


    def to_dict(self):
        return {
            "journey_id": self.journey_id,  # IMPORTANT
            "destination": self.destination,
            "start_date": str(self.start_date),
            "end_date": str(self.end_date),
            "budget": self.budget,
            "people": self.people,
            "notes": self.notes
        }
