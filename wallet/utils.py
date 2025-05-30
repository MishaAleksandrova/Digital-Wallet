from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
import requests
from django.conf import settings

signer = TimestampSigner()

def generate_email_token(email):
    return signer.sign(email)

def verify_email_token(token, max_age=86400):
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None

def get_exchange_rate(from_currency, to_currency):
    api_key = settings.FREE_CURRENCY_API_KEY
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&base_currency={from_currency}&currencies={to_currency}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['data'][to_currency]
    except Exception as ex:
        print("Exchange rate fetch error", ex)
        return None
