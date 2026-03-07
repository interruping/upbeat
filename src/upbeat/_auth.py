from __future__ import annotations

import hashlib
import uuid
from urllib.parse import unquote, urlencode

import jwt


class Credentials:
    access_key: str
    secret_key: str

    def __init__(self, access_key: str, secret_key: str) -> None:
        if not access_key or not access_key.strip():
            raise ValueError("access_key must not be empty or blank")
        if not secret_key or not secret_key.strip():
            raise ValueError("secret_key must not be empty or blank")
        if " " in access_key or "\t" in access_key:
            raise ValueError("access_key must not contain whitespace")
        if " " in secret_key or "\t" in secret_key:
            raise ValueError("secret_key must not contain whitespace")
        self.access_key = access_key
        self.secret_key = secret_key

    def __repr__(self) -> str:
        if len(self.access_key) > 6:
            masked = f"{self.access_key[:3]}...{self.access_key[-3:]}"
        else:
            masked = self.access_key[:1] + "***"
        return f"Credentials(access_key='{masked}', secret_key='***')"


def build_query_string(params: dict[str, object]) -> str:
    if not params:
        return ""
    return unquote(urlencode(params, doseq=True))


def build_jwt(credentials: Credentials, query_string: str = "") -> str:
    payload: dict[str, str] = {
        "access_key": credentials.access_key,
        "nonce": str(uuid.uuid4()),
    }

    if query_string:
        query_hash = hashlib.sha512(query_string.encode("utf-8")).hexdigest()
        payload["query_hash"] = query_hash
        payload["query_hash_alg"] = "SHA512"

    return jwt.encode(payload, credentials.secret_key, algorithm="HS512")


def build_auth_header(credentials: Credentials, query_string: str = "") -> str:
    return f"Bearer {build_jwt(credentials, query_string)}"
