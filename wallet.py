from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

class WalletError(ValueError):
    pass

class Wallet:
    def __init__(self, name, currency="RUB", balance=0):
        self.name = name 
        self.currency = currency
        self.balance = self.parse_money(balance)

    @staticmethod
    def parse_money(value):
        try:
            amount = Decimal(str(value))
            amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            raise WalletError("Сумма должна быть числом")
        
        return amount
        
    def top_up(self, amount):
        amount = self.parse_money(amount)
        if amount <= 0: 
            raise WalletError("Сумма пополнения должна быть больше нуля")
        self.balance += amount
        return self.balance
    
    def spend(self, amount):
        amount = self.parse_money(amount)
        if amount <= 0:
            raise WalletError("Сумма списания должна быть больше нуля")
        if self.balance < amount:
            raise WalletError("Недостаточно средств для платежа")
        self.balance -= amount
        return self.balance

class ExchangeAccount:
    def __init__(self, username):
        self.username = username
        self.wallets = {} 
    
    @staticmethod
    def validate_wallet_name(wallet_name):
        if not isinstance(wallet_name, str):
            raise WalletError("Имя кошелька должно быть строкой")

        wallet_name = wallet_name.strip()

        if not wallet_name:
            raise WalletError("Имя кошелька не может быть пустым")

        return wallet_name  

    def create_rub_wallet(self, wallet_name, start_balance="0.0"):
        wallet_name = self.validate_wallet_name(wallet_name)
        if wallet_name in self.wallets:
            raise WalletError(f"Кошелек с именем '{wallet_name}' уже существует")

        parsed_balance = Wallet.parse_money(start_balance)
        if parsed_balance < 0:
            raise WalletError("Стартовый баланс не может быть отрицательным")
            
        self.wallets[wallet_name] = Wallet(wallet_name, "RUB", parsed_balance)

        return self.wallets[wallet_name]
        
    def get_wallet(self, wallet_name):
        if wallet_name not in self.wallets: 
            raise WalletError(f"Кошелька '{wallet_name}' не существует")
        return self.wallets[wallet_name]


