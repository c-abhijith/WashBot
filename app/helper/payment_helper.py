import stripe
import razorpay
import paypalrestsdk
from flask import current_app
import json

class PaymentGateway:
    @staticmethod
    def create_stripe_payment(amount, currency='USD', payment_method_id=None):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                payment_method=payment_method_id,
                confirmation_method='manual',
                confirm=True if payment_method_id else False
            )
            return {
                'success': True,
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_razorpay_payment(amount, currency='INR'):
        client = razorpay.Client(
            auth=(current_app.config['RAZORPAY_KEY_ID'],
                  current_app.config['RAZORPAY_KEY_SECRET'])
        )
        try:
            order = client.order.create({
                'amount': int(amount * 100),
                'currency': currency,
                'payment_capture': '1'
            })
            return {
                'success': True,
                'order_id': order['id']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_paypal_payment(amount, currency='USD', return_url=None, cancel_url=None):
        paypalrestsdk.configure({
            "mode": current_app.config['PAYPAL_MODE'],
            "client_id": current_app.config['PAYPAL_CLIENT_ID'],
            "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": currency
                },
                "description": "CarWash Service Payment"
            }]
        })

        try:
            if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                        return {
                            'success': True,
                            'payment_id': payment.id,
                            'approval_url': link.href
                        }
            return {
                'success': False,
                'error': 'Failed to create PayPal payment'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def verify_payment(payment_method, payment_data):
        if payment_method == 'stripe':
            return PaymentGateway._verify_stripe_payment(payment_data)
        elif payment_method == 'razorpay':
            return PaymentGateway._verify_razorpay_payment(payment_data)
        elif payment_method == 'paypal':
            return PaymentGateway._verify_paypal_payment(payment_data)
        return False

    @staticmethod
    def _verify_stripe_payment(payment_data):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        try:
            intent = stripe.PaymentIntent.retrieve(payment_data['payment_intent_id'])
            return intent.status == 'succeeded'
        except Exception:
            return False

    @staticmethod
    def _verify_razorpay_payment(payment_data):
        client = razorpay.Client(
            auth=(current_app.config['RAZORPAY_KEY_ID'],
                  current_app.config['RAZORPAY_KEY_SECRET'])
        )
        try:
            return client.utility.verify_payment_signature(payment_data)
        except Exception:
            return False

    @staticmethod
    def _verify_paypal_payment(payment_data):
        try:
            payment = paypalrestsdk.Payment.find(payment_data['paymentId'])
            if payment.execute({'payer_id': payment_data['PayerID']}):
                return True
            return False
        except Exception:
            return False 