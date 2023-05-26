import json
from typing import Any

from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
from flask import current_app
from jose import jwe


def decrypt(token: str) -> dict[str, Any]:
    with current_app.app_context():
        next_auth_secret = current_app.config.get('NEXT_AUTH_SECRET_KEY')
        next_auth_encryption_key = current_app.config.get('NEXT_AUTH_ENCRYPTION_KEY')
        encryption_key = __get_derived_encryption_key(next_auth_secret, next_auth_encryption_key)
        payload_str = jwe.decrypt(token, encryption_key).decode()
        payload: dict[str, Any] = json.loads(payload_str)

        return payload


def __get_derived_encryption_key(secret: str, encryption_key: str) -> Any:
    context = str.encode(encryption_key)
    return HKDF(
        master=secret.encode(),
        key_len=32,
        salt="".encode(),
        hashmod=SHA256,
        num_keys=1,
        context=context,
    )
