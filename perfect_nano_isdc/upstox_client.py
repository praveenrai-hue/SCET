from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


UPSTOX_API_BASE = "https://api.upstox.com"


class UpstoxAPIError(RuntimeError):
    """Raised when the Upstox API returns an error payload or non-2xx code."""


@dataclass(frozen=True)
class UpstoxConfig:
    access_token: str
    api_base: str = UPSTOX_API_BASE

    @staticmethod
    def from_env() -> "UpstoxConfig":
        token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
        if not token:
            raise ValueError("UPSTOX_ACCESS_TOKEN is missing. Export it before running.")
        return UpstoxConfig(access_token=token)


class UpstoxClient:
    def __init__(self, config: UpstoxConfig, timeout: int = 12) -> None:
        self.config = config
        self.timeout = timeout

    def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.config.api_base}{path}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.config.access_token}",
        }
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if not response.ok:
            raise UpstoxAPIError(f"HTTP {response.status_code}: {response.text}")

        payload = response.json()
        status = str(payload.get("status", "")).lower()
        if status and status != "success":
            raise UpstoxAPIError(f"API failure: {payload}")
        return payload

    def get_ltp(self, instrument_key: str) -> Dict[str, Any]:
        """
        Fetches last traded price and related quote fields.
        instrument_key example: 'NSE_INDEX|Nifty Bank'.
        """
        return self._request(
            "GET",
            "/v2/market-quote/ltp",
            params={"instrument_key": instrument_key},
        )

    def get_ohlc(self, instrument_key: str, interval: str = "30minute") -> Dict[str, Any]:
        """
        Fetches intraday OHLC candles.
        interval examples: '1minute', '30minute', 'day'.
        """
        return self._request(
            "GET",
            "/v2/historical-candle/intraday",
            params={"instrument_key": instrument_key, "interval": interval},
        )

    def get_option_chain(self, instrument_key: str, expiry_date: str) -> Dict[str, Any]:
        """Fetches option chain for a given underlying and expiry date (YYYY-MM-DD)."""
        return self._request(
            "GET",
            "/v2/option/chain",
            params={"instrument_key": instrument_key, "expiry_date": expiry_date},
        )
