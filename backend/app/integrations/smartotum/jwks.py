# backend/app/integrations/smartotum/jwks.py
from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient, InvalidTokenError, PyJWKClientError
from flask import current_app

@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    jwks_url = current_app.config["SMARTOTUM_JWKS_URL"]
    return PyJWKClient(jwks_url)

def decode_smartotum_token(token: str) -> dict[str, Any]:
    try:
        client = _jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
    except PyJWKClientError:
        _jwks_client.cache_clear()
        client = _jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=current_app.config["SMARTOTUM_ISSUER"],
        options={"verify_aud": False},
    ) #return payload of the token: sub, exp, st-role, st-perm