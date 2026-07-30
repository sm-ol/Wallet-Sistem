import pytest
from decimal import Decimal
from wallet import Wallet, ExchangeAccount, WalletError

@pytest.fixture
def empty_account():
    return ExchangeAccount(username="TestUser")


@pytest.mark.parametrize(
    "name, currency, balance, operation, amount, itog",
    [
        pytest.param("Anna", "RUB", 1000, "spend", 200, Decimal("800.00"), id="spend_balance"),
        pytest.param("Kate", "RUB", 1000, "top_up", 200, Decimal("1200.00"), id="top_up_balance"),
        pytest.param("Dima", "RUB", 1000, "spend", "200.50", Decimal("799.50"), id="float_spend_balance"),   
        pytest.param("Tim", "RUB", 1000, "top_up", "200.50", Decimal("1200.50"), id="float_top_up_balance"), 
    ]
)
def test_wallet_happy_paths(name, currency, balance, operation, amount, itog):
    wallet = Wallet(name=name, currency=currency, balance=balance)
    returned_balance = getattr(wallet, operation)(amount)
            
    assert returned_balance == itog  
    assert wallet.balance == itog    

def test_create_wallet_returns_wallet(empty_account):
    wallet = empty_account.create_rub_wallet("Main", "500.00")
    
    assert "Main" in empty_account.wallets
    assert wallet.name == "Main"
    assert wallet.currency == "RUB"
    assert wallet.balance == Decimal("500.00")


def test_duplicate_wallet_raises(empty_account):
    empty_account.create_rub_wallet("Main", "100.00")

    with pytest.raises(WalletError, match="уже существует"):
        empty_account.create_rub_wallet("Main", "200.00")


def test_empty_wallet_name_raises(empty_account):
    with pytest.raises(WalletError, match="не может быть пустым"):
        empty_account.create_rub_wallet("   ", "100.00")


def test_wallet_name_must_be_string_raises(empty_account):
    with pytest.raises(WalletError, match="должно быть строкой"):
        empty_account.create_rub_wallet(12345, "100.00")


def test_wallet_name_is_stripped(empty_account):
    wallet = empty_account.create_rub_wallet("  Main  ", "100.00")
    
    assert wallet.name == "Main"
    assert "Main" in empty_account.wallets
    assert "  Main  " not in empty_account.wallets


def test_negative_start_balance_raises(empty_account):
    with pytest.raises(WalletError, match="Стартовый баланс не может быть отрицательным"):
        empty_account.create_rub_wallet("Main", "-1.00")


def test_zero_top_up_raises():
    wallet = Wallet("Main", balance="100.00")

    with pytest.raises(WalletError, match="больше нуля"):
        wallet.top_up("0")
        
    assert wallet.balance == Decimal("100.00")


def test_negative_top_up_raises():
    wallet = Wallet("Main", balance="100.00")

    with pytest.raises(WalletError, match="больше нуля"):
        wallet.top_up("-10.00")
        
    assert wallet.balance == Decimal("100.00")


def test_zero_spend_raises():
    wallet = Wallet("Main", balance="100.00")

    with pytest.raises(WalletError, match="больше нуля"):
        wallet.spend("0")
        
    assert wallet.balance == Decimal("100.00")


def test_overspend_raises_and_balance_unchanged():
    wallet = Wallet("Main", balance="100.00")

    with pytest.raises(WalletError, match="Недостаточно средств для платежа"):
        wallet.spend("150.00")

    assert wallet.balance == Decimal("100.00") 


def test_get_non_existent_wallet_error(empty_account):
    with pytest.raises(WalletError, match="не существует"):
        empty_account.get_wallet("HiddenWallet")


def test_decimal_precision():
    wallet = Wallet("Main", balance="0.00")

    wallet.top_up("0.10")
    wallet.top_up("0.20")

    assert wallet.balance == Decimal("0.30")


