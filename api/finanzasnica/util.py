import secrets
from django.conf import settings
from django.utils.crypto import salted_hmac

def generate_code():
    return secrets.token_hex(4).upper()

def generate_secret_key(value):
    salt = 'mahq$ZbFl!2G6y+8!.mPL%<?fnk:^LMM'
    secret_value = str(value)
    hmac = salted_hmac( salt, secret_value )
    return hmac.hexdigest()