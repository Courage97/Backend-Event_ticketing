import requests
from django.conf import settings
from django.core.files import File
import qrcode
from io import BytesIO

def initialize_paystack_transaction(email, amount, metadata, subaccount=None, callback_url=None):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": email,
        "amount": int(amount * 100),
        "metadata": metadata,
    }

    if subaccount:
        data["subaccount"] = subaccount

    if callback_url:
        data["callback_url"] = callback_url

    response = requests.post(url, json=data, headers=headers)
    return response.json()



# Manual payment verification utils
def verify_paystack_transaction(reference):
    url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    return response.json()

# To generate qr_code
def generate_qr_code(data):
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer)
    return File(buffer, name='qr.png')


import requests
from django.conf import settings

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
        "percentage_charge": 0,  # 0% charge = full payout to organizer
        "description": "Payout subaccount for event organizer",
        "primary_contact_email": email,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
