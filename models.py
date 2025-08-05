import json
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime

Base = declarative_base()


class ProcessedRequest(Base):
    __tablename__ = "processed_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, index=True, nullable=False)
    payload = Column(Text, nullable=False)
    worker_id = Column(Integer, nullable=False)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_payload(self, payload_dict):
        """Convert dict to JSON string for storage"""
        self.payload = json.dumps(payload_dict)

    def get_payload(self):
        """Convert JSON string back to dict"""
        return json.loads(self.payload) if self.payload else {}

    def set_result(self, result_dict):
        """Convert dict to JSON string for storage"""
        self.result = json.dumps(result_dict)

    def get_result(self):
        """Convert JSON string back to dict"""
        return json.loads(self.result) if self.result else {}
