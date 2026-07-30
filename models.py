from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True) 
    username = Column(String(50), unique=True, index=True, nullable=False)
    wallets = relationship("Wallet", back_populates="owner", cascade="all, delete-orphan")

class Wallet(Base):
    __tablename__="wallets"

    id = Column(Integer, primary_key=True) 
    name = Column(String(50), index=True, nullable=False)
    currency = Column(String(10), default="RUB", nullable=False)
    balance = Column(Numeric(precision=10, scale=2, asdecimal=True), default=0.0, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="wallets")

    __table_args__ = (UniqueConstraint('user_id', 'name', name='uix_user_wallet_name'),)




