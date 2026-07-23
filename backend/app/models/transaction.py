from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key — every transaction belongs to one user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    bank = Column(String)

    account_number = Column(String)

    transaction_type = Column(String)  # "Debit" or "Credit"

    amount = Column(Float)

    date = Column(String)  # stored as string from SMS e.g. "22/07/26"

    merchant = Column(String)

    upi_reference = Column(String)

    balance = Column(Float)

    category = Column(String, default="Others")  # for Category Management (Phase 5 Module 8)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to User
    owner = relationship("User", back_populates="transactions")
