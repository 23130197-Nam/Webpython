from abc import ABC, abstractmethod
from typing import Dict, Type
from datetime import datetime
from .models import Payment

class PaymentGateway(ABC):
    @abstractmethod
    def process_transaction(self, amount: float) -> str:
        pass

class MockBankGateway(PaymentGateway):
    def process_transaction(self, amount: float) -> str:
        return f"BT_REF_{int(datetime.now().timestamp())}"

class MockVNPayGateway(PaymentGateway):
    def process_transaction(self, amount: float) -> str:
        return f"VNPAY_REF_{int(datetime.now().timestamp())}"

class PaymentStrategy(ABC):
    gateway: PaymentGateway
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
    @abstractmethod
    def execute_payment(self, order_id: str, amount: float, currency: str) -> Payment:
        pass

class BankTransferPayment(PaymentStrategy):
    def execute_payment(self, order_id: str, amount: float, currency: str) -> Payment:
        provider_ref = self.gateway.process_transaction(amount)
        return Payment.objects.create(
            order_id=order_id,
            method="BANK_TRANSFER",
            providerReference=provider_ref,
            amount=amount,
            currency=currency,
            status='COMPLETED', 
            paidAt=datetime.now()
        )

class VNPayPayment(PaymentStrategy):
    def execute_payment(self, order_id: str, amount: float, currency: str) -> Payment:
        provider_ref = self.gateway.process_transaction(amount)
        return Payment.objects.create(
            order_id=order_id,
            method="VNPAY",
            providerReference=provider_ref,
            amount=amount,
            currency=currency,
            status='PENDING',
        )
    
class CODPayment(PaymentStrategy):
    def execute_payment(self, order_id: str, amount: float, currency: str) -> Payment:
        return Payment.objects.create(
            order_id=order_id,
            method="COD",
            providerReference=f"COD_{order_id}",
            amount=amount,
            currency=currency,
            status='PENDING',
        )

class PaymentFactory:
    MAP_CODE_TO_METHOD = {"1": "VNPAY", "2": "BANK_TRANSFER", "3": "COD"}
    strategies: Dict[str, Type[PaymentStrategy]] = {
        "BANK_TRANSFER": BankTransferPayment,
        "VNPAY": VNPayPayment,
        "COD": CODPayment,
    }

    @staticmethod
    def get_strategy(method: str) -> PaymentStrategy:
        m_code = str(method)
        method_name = PaymentFactory.MAP_CODE_TO_METHOD.get(m_code)
        if not method_name:
            method_name = m_code.upper()

        strategy_class = PaymentFactory.strategies.get(method_name)
        if not strategy_class:
            raise ValueError(f"Payment method '{method}' is not supported.")
        
        gateway = None
        if method_name == "BANK_TRANSFER":
            gateway = MockBankGateway()
        elif method_name == "VNPAY":
            gateway = MockVNPayGateway()
        elif method_name == "COD":
            gateway = None
        else:
            raise NotImplementedError(f"Gateway cho {method_name} chưa được thiết lập.")
        return strategy_class(gateway)

class PaymentService:
    def __init__(self, factory: PaymentFactory = PaymentFactory):
        self.factory = factory
    @staticmethod
    def create_payment(method: str, order_id: str, amount: float, currency: str = "VND") -> Payment:
        strategy = PaymentFactory.get_strategy(method)
        new_payment = strategy.execute_payment(order_id, amount, currency)
        return new_payment