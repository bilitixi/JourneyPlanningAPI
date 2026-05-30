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
    user = relationship("User", backref="journeys")
    
    def to_dict(self):
        return {
            'journey_id': self.journey_id,
            'user_id': self.user_id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': float(self.budget) if self.budget else None,
            'people': self.people,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
