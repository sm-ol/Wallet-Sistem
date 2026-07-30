from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
import models
import schemas

router = APIRouter(prefix="/wallets", tags=["Wallets"])

@router.post("/user/{username}/", response_model=schemas.WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet(username: str, wallet_data: schemas.WalletCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    wallet_name = wallet_data.name.strip()
    duplicate = db.query(models.Wallet).filter(models.Wallet.user_id == user.id, models.Wallet.name == wallet_name).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Кошелек с таким именем уже существует у этого пользователя")

    new_wallet = models.Wallet(name=wallet_name, balance=wallet_data.start_balance, user_id=user.id)
    db.add(new_wallet)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Кошелек с таким именем уже существует у этого пользователя")
        
    db.refresh(new_wallet)

    new_wallet.owner_username = user.username
    return new_wallet

@router.post("/top-up/")
def top_up_wallet(tx_data: schemas.WalletTransaction, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == tx_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == user.id, 
        models.Wallet.name == tx_data.wallet_name
    ).with_for_update().first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Кошелек не найден")
        
    wallet.balance += tx_data.amount
    db.commit()
    db.refresh(wallet)
    return {"name": wallet.name, "new_balance": str(wallet.balance)}

@router.post("/spend/")
def spend_wallet(tx_data: schemas.WalletTransaction, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == tx_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    wallet = db.query(models.Wallet).filter(
        models.Wallet.user_id == user.id, 
        models.Wallet.name == tx_data.wallet_name
    ).with_for_update().first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Кошелек не найден")
        
    if wallet.balance < tx_data.amount:
        raise HTTPException(status_code=400, detail="Недостаточно средств")
        
    wallet.balance -= tx_data.amount
    db.commit()
    db.refresh(wallet)
    return {"name": wallet.name, "new_balance": str(wallet.balance)}


@router.get("/{username}/", response_model=list[schemas.WalletResponse])
def get_user_wallets(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    wallets = user.wallets

    for wallet in wallets:
        wallet.owner_username = user.username
        
    return wallets
