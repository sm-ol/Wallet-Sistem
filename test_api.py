import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_wallet_system.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "готово к работе"}


def test_user_creation_and_duplicate():
    response = client.post("/users/", json={"username": "  Olya  "})
    assert response.status_code == 201
    assert response.json()["username"] == "Olya"
    assert "id" in response.json()

    duplicate_response = client.post("/users/", json={"username": "Olya"})
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Пользователь с таким именем уже существует"


def test_wallet_workflow():
    client.post("/users/", json={"username": "Kate"})

    wallet_data = {"name": "  MainWallet  ", "start_balance": "100.50"}
    response = client.post("/wallets/user/Kate/", json=wallet_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "MainWallet" 
    assert data["balance"] == "100.50"
    assert data["owner_username"] == "Kate"

    top_up_data = {"username": "Kate", "wallet_name": "MainWallet", "amount": "50.25"}
    response = client.post("/wallets/top-up/", json=top_up_data)
    assert response.status_code == 200
    assert response.json()["new_balance"] == "150.75"

    spend_data = {"username": "Kate", "wallet_name": "MainWallet", "amount": "40.00"}
    response = client.post("/wallets/spend/", json=spend_data)
    assert response.status_code == 200
    assert response.json()["new_balance"] == "110.75"


def test_wallet_insufficient_funds():
    client.post("/users/", json={"username": "Mari"})
    client.post("/wallets/user/Mari/", json={"name": "Cart", "start_balance": "10.00"})

    spend_data = {"username": "Mari", "wallet_name": "Cart", "amount": "50.00"}
    response = client.post("/wallets/spend/", json=spend_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Недостаточно средств"


def test_get_user_wallets():
    client.post("/users/", json={"username": "Vlad"})
    client.post("/wallets/user/Vlad/", json={"name": "W1", "start_balance": "10.00"})
    client.post("/wallets/user/Vlad/", json={"name": "W2", "start_balance": "20.00"})

    response = client.get("/wallets/Vlad/")
    assert response.status_code == 200
    
    wallets = response.json()
    assert len(wallets) == 2
    assert wallets[0]["name"] == "W1"
    assert wallets[1]["name"] == "W2"


