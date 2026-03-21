"""Tests for authentication logic in the openHAB connection handler."""
from __future__ import annotations

from HABApp.openhab.connection.plugins.websockets import WebsocketPlugin


class TestBuildToken:
    """Tests for WebsocketPlugin._build_token."""

    def test_token_in_login(self):
        from aiohttp import BasicAuth
        auth = BasicAuth('oh.mytoken.abc', '')
        assert WebsocketPlugin._build_token(auth) == 'oh.mytoken.abc'

    def test_token_in_password(self):
        from aiohttp import BasicAuth
        auth = BasicAuth('', 'oh.mytoken.abc')
        assert WebsocketPlugin._build_token(auth) == 'oh.mytoken.abc'

    def test_basic_auth_fallback(self):
        from base64 import b64encode
        from aiohttp import BasicAuth
        auth = BasicAuth('admin', 'secret')
        expected = b64encode(b'admin:secret').decode()
        assert WebsocketPlugin._build_token(auth) == expected


class TestTokenResolution:
    """Tests for the token resolution logic used in handler.py on_setup.

    When a token is found in the legacy 'user' or 'password' config fields it
    must be migrated to Bearer auth with a deprecation warning.  The returned
    ``legacy_field`` name is non-None only when migration occurred.
    """

    class _Config:
        def __init__(self, token='', user='', password=''):
            self.token = token
            self.user = user
            self.password = password

    def _resolve(self, config) -> tuple[str | None, str | None]:
        """Replicates the token resolution in handler.py on_setup."""
        bearer = config.token or None
        legacy_field = None
        if not bearer:
            for fname, fval in (('user', config.user), ('password', config.password)):
                if fval.startswith('oh.'):
                    bearer = fval
                    legacy_field = fname
                    break
        return bearer, legacy_field

    def test_explicit_token_field(self):
        cfg = self._Config(token='oh.explicit.token')
        bearer, legacy = self._resolve(cfg)
        assert bearer == 'oh.explicit.token'
        assert legacy is None

    def test_token_in_user_migrated(self):
        """Token placed in 'user' is detected and migration flag is set."""
        cfg = self._Config(user='oh.legacy_user_token')
        bearer, legacy = self._resolve(cfg)
        assert bearer == 'oh.legacy_user_token'
        assert legacy == 'user'

    def test_token_in_password_migrated(self):
        """Token placed in 'password' is detected and migration flag is set."""
        cfg = self._Config(password='oh.legacy_pass_token')
        bearer, legacy = self._resolve(cfg)
        assert bearer == 'oh.legacy_pass_token'
        assert legacy == 'password'

    def test_explicit_token_takes_precedence_over_user(self):
        """Explicit token field wins; no migration flag when both are set."""
        cfg = self._Config(token='oh.explicit', user='oh.user_token')
        bearer, legacy = self._resolve(cfg)
        assert bearer == 'oh.explicit'
        assert legacy is None

    def test_plain_credentials_no_token(self):
        """Plain username/password: no bearer token resolved."""
        cfg = self._Config(user='admin', password='secret')
        bearer, legacy = self._resolve(cfg)
        assert bearer is None
        assert legacy is None
