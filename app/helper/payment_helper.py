import stripe
import razorpay
import paypalrestsdk
from flask import current_app
import json

class PaymentGateway:
    @staticmethod
    def create_stripe_payment(amount, currency='USD', payment_method_id=None):
        try:
            # For testing, return mock payment data
            return {
                'success': True,
                'payment_intent_id': 'pi_mock_' + str(amount),
                'client_secret': 'mock_secret',
                'amount': amount,
                'currency': currency,
                'status': 'requires_payment_method'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_razorpay_payment(amount, currency='INR'):
        try:
            # For testing, return mock order data
            return {
                'success': True,
                'order_id': 'order_mock_' + str(amount),
                'amount': amount,
                'currency': currency,
                'status': 'created'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_paypal_payment(amount, currency='USD', return_url=None, cancel_url=None):
        try:
            # For testing, return mock payment data
            return {
                'success': True,
                'payment_id': 'pay_mock_' + str(amount),
                'approval_url': 'https://mock-paypal.com/approve',
                'amount': amount,
                'currency': currency,
                'status': 'created'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def verify_payment(payment_method, payment_data):
        # For testing, always return True
        return True

    @staticmethod
    def _verify_stripe_payment(payment_data):
        # For testing, always return True
        return True

    @staticmethod
    def _verify_razorpay_payment(payment_data):
        # For testing, always return True
        return True

    @staticmethod
    def _verify_paypal_payment(payment_data):
        # For testing, always return True
        return True 