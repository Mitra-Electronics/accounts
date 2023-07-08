import pyotp

def gen(handle: str):
    key = pyotp.random_base32()
    totp = pyotp.totp.TOTP(key)
    url = totp.provisioning_uri(name='Accounts: '+handle, issuer_name='Accounts')
    return url