import hashlib
import uuid

import jwt
import pytest

from upbeat._auth import (
    Credentials,
    build_auth_header,
    build_jwt,
    build_query_string,
)

SECRET = "test-secret-key"
ACCESS = "test-access-key"


# ── Credentials ──────────────────────────────────────────────────────────


class TestCredentials:
    def test_valid_creation(self):
        creds = Credentials(ACCESS, SECRET)
        assert creds.access_key == ACCESS
        assert creds.secret_key == SECRET

    def test_empty_access_key(self):
        with pytest.raises(ValueError, match="access_key"):
            Credentials("", SECRET)

    def test_blank_access_key(self):
        with pytest.raises(ValueError, match="access_key"):
            Credentials("   ", SECRET)

    def test_empty_secret_key(self):
        with pytest.raises(ValueError, match="secret_key"):
            Credentials(ACCESS, "")

    def test_blank_secret_key(self):
        with pytest.raises(ValueError, match="secret_key"):
            Credentials(ACCESS, "   ")

    def test_whitespace_in_access_key(self):
        with pytest.raises(ValueError, match="access_key"):
            Credentials("key with space", SECRET)

    def test_whitespace_in_secret_key(self):
        with pytest.raises(ValueError, match="secret_key"):
            Credentials(ACCESS, "key\twith\ttab")

    def test_repr_masks_secret(self):
        creds = Credentials(ACCESS, SECRET)
        r = repr(creds)
        assert SECRET not in r
        assert "***" in r
        assert "tes...key" in r

    def test_repr_short_access_key(self):
        creds = Credentials("abcdef", SECRET)
        r = repr(creds)
        assert "a***" in r
        assert SECRET not in r


# ── build_query_string ───────────────────────────────────────────────────


class TestBuildQueryString:
    def test_simple_params(self):
        qs = build_query_string({"market": "KRW-BTC", "limit": 10})
        assert "market=KRW-BTC" in qs
        assert "limit=10" in qs

    def test_array_params(self):
        qs = build_query_string({"states[]": ["wait", "watch"]})
        assert qs == "states[]=wait&states[]=watch"

    def test_mixed_params(self):
        qs = build_query_string(
            {"market": "KRW-BTC", "states[]": ["wait", "watch"]}
        )
        assert "market=KRW-BTC" in qs
        assert "states[]=wait" in qs
        assert "states[]=watch" in qs

    def test_empty_dict(self):
        assert build_query_string({}) == ""


# ── build_jwt ────────────────────────────────────────────────────────────


class TestBuildJwt:
    def test_without_query_string(self):
        creds = Credentials(ACCESS, SECRET)
        token = build_jwt(creds)
        payload = jwt.decode(token, SECRET, algorithms=["HS512"])
        assert payload["access_key"] == ACCESS
        assert "nonce" in payload
        uuid.UUID(payload["nonce"])  # valid UUID4
        assert "query_hash" not in payload
        assert "query_hash_alg" not in payload

    def test_with_query_string(self):
        creds = Credentials(ACCESS, SECRET)
        qs = "market=KRW-BTC&limit=10"
        token = build_jwt(creds, qs)
        payload = jwt.decode(token, SECRET, algorithms=["HS512"])
        assert payload["access_key"] == ACCESS
        assert payload["query_hash_alg"] == "SHA512"
        expected_hash = hashlib.sha512(qs.encode("utf-8")).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_nonce_is_unique(self):
        creds = Credentials(ACCESS, SECRET)
        t1 = build_jwt(creds)
        t2 = build_jwt(creds)
        p1 = jwt.decode(t1, SECRET, algorithms=["HS512"])
        p2 = jwt.decode(t2, SECRET, algorithms=["HS512"])
        assert p1["nonce"] != p2["nonce"]


# ── build_auth_header ────────────────────────────────────────────────────


class TestBuildAuthHeader:
    def test_bearer_prefix(self):
        creds = Credentials(ACCESS, SECRET)
        header = build_auth_header(creds)
        assert header.startswith("Bearer ")

    def test_valid_jwt_in_header(self):
        creds = Credentials(ACCESS, SECRET)
        header = build_auth_header(creds)
        token = header.removeprefix("Bearer ")
        payload = jwt.decode(token, SECRET, algorithms=["HS512"])
        assert payload["access_key"] == ACCESS

    def test_with_query_string(self):
        creds = Credentials(ACCESS, SECRET)
        qs = "market=KRW-BTC"
        header = build_auth_header(creds, qs)
        token = header.removeprefix("Bearer ")
        payload = jwt.decode(token, SECRET, algorithms=["HS512"])
        assert "query_hash" in payload
