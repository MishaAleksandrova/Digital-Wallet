from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

signer = TimestampSigner()

def generate_email_token(email):
    return signer.sign(email)

def verify_email_token(token, max_age=86400):
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None