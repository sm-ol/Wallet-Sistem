from pydantic import BaseModel, Field
from decimal import Decimal

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class WalletCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    start_balance: Decimal = Field(default=Decimal("0.0"), ge=0)


class WalletTransaction(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    wallet_name: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., gt=0)

class WalletResponse(BaseModel):
    id: int
    name: str
    balance: Decimal
    currency: str
    owner_username: str

    class Config:
        from_attributes = True
