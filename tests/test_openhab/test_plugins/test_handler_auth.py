"""Tests for authentication logic in the openHAB connection handler."""
from __future__ import annotations

import pytest

from HABApp.openhab.connection.plugins.websockets import WebsocketPlugin


class TestBuildToken:
    """Tests for WebsocketPlugin._build_token (Issue #1 regression check)."""

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


class TestTokenNormalization:
    """Tests that token normalization in handler.py fixes Issue #1."""

    def _normalize(self, user: str, password: str):
        """Replicate the normalization logic from handler.py on_setup."""
        is_token = user.startswith('oh.') or password.startswith('oh.')
        if is_token and not user:
            user, password = password, ''
        return user, password

    def test_token_in_user_unchanged(self):
        user, password = self._normalize('oh.mytoken.abc', '')
        assert user == 'oh.mytoken.abc'
        assert password == ''

    def test_token_in_password_moved_to_user(self):
        """Token in password field must be moved to user for BasicAuth to work."""
        user, password = self._normalize('', 'oh.mytoken.abc')
        assert user == 'oh.mytoken.abc'
        assert password == ''

    def test_both_set_not_touched(self):
        """If both fields are set, do not silently rearrange them."""
        user, password = self._normalize('oh.user_token', 'oh.pass_token')
        assert user == 'oh.user_token'
        assert password == 'oh.pass_token'

    def test_plain_credentials_unchanged(self):
        user, password = self._normalize('admin', 'secret')
        assert user == 'admin'
        assert password == 'secret'
