from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
import requests

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
    url = f"https://api.freecurrencyapi.com/v1/latest"
    params = {
        "apikey": "fca_live_RCxS9tzbd6gPI1EK5K1YsJn9ANZgSwVzZLVfkaVZ",
        "base_currency": from_currency,
    }
    responses = requests.get(url, params=params)
    data = responses.json()

    if 'data' in data:
        rates = data['data']
        if to_currency in rates:
            return rates[to_currency]
    return None