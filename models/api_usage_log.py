from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base


class APIUsageLog(Base):
    __tablename__ = 'api_usage_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    parameters = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationship with User
    user = relationship("User", backref="api_logs")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'parameters': self.parameters,
            'status_code': self.status_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
