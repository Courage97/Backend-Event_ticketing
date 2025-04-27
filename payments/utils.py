import requests
from django.conf import settings
from decimal import Decimal

def initialize_paystack_transaction(email, amount, metadata, subaccount=None, transaction_charge=None, callback_url=None):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": email,
        "amount": int(amount * 100),  # convert to kobo
        "metadata": metadata,
    }

    if callback_url:
        payload["callback_url"] = callback_url

    if subaccount:
        payload["subaccount"] = subaccount
        payload["bearer"] = "account"  # Organizer bears charges
        payload["transaction_charge"] = int(amount * Decimal('0.05') * 100)  # 5% to admin

    response = requests.post(url, json=payload, headers=headers)
    return response.json()



def create_paystack_subaccount(bank_code, account_number, business_name, email):
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "business_name": business_name,
        "settlement_bank": bank_code,
        "account_number": account_number,
        "percentage_charge": 0,
        "description": "Organizer Payout Account",
        "primary_contact_email": email,
    }
    res = requests.post(url, json=payload, headers=headers)
    return res.json()
