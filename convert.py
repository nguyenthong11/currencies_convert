"""
Currency conversion module for Fixer.io API.
Run with: python convert.py
"""
import os
import time
import requests
from streamlit import secrets

# --- Simple in-memory cache with TTL ---
_CONVERSION_CACHE: dict[tuple, tuple[dict, float]] = {}
_CACHE_TTL_SECONDS = 86400  # Cache conversion results for 24 hours


def _get_cache_key(amount: float, from_currency: str, to_currency: str, method: str) -> tuple:
    """Generate a cache key from conversion parameters."""
    return (from_currency, to_currency, method, round(amount, 2))


def _get_cached(key: tuple) -> dict | None:
    """Retrieve cached result if still valid."""
    if key in _CONVERSION_CACHE:
        result, timestamp = _CONVERSION_CACHE[key]
        if time.time() - timestamp < _CACHE_TTL_SECONDS:
            return result
        # Expired - remove it
        del _CONVERSION_CACHE[key]
    return None


def _set_cached(key: tuple, result: dict) -> None:
    """Store result in cache with current timestamp."""
    _CONVERSION_CACHE[key] = (result, time.time())


def _get_access_key() -> str:
    access_key = secrets.get("FIXER_IO_ACCESS_KEY")
    if not access_key:
        raise RuntimeError("FIXER_IO_ACCESS_KEY is not set in the environment")
    return access_key


def convert(
    amount: float = 1.0,
    from_currency: str = "EUR",
    to_currency: str = "USD",
    method: str = "latest",
) -> dict:
    """
    Convert currencies via Fixer.io and return the parsed JSON response.

    Methods:
      - "latest":  GET /latest?base=EUR&symbols=... then divide manually.
                   Reliable on Fixer's free tier (which locks base=EUR).
                   Returns a synthetic response dict shaped like /convert.
      - "convert": GET /convert?from=...&to=...&amount=...
                   Direct, but on free-tier keys the rate is often a frozen
                   historical date rather than the current rate.

    Returns the full response dict so the caller can inspect success, result,
    info, etc. Raises requests.exceptions.RequestException on network failure.
    """
    if method not in ("latest", "convert"):
        raise ValueError(f"method must be 'latest' or 'convert', got {method!r}")

    # Check cache first
    cache_key = _get_cache_key(amount, from_currency, to_currency, method)
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    access_key = _get_access_key()

    if method == "convert":
        url = (
            f"https://data.fixer.io/api/convert"
            f"?access_key={access_key}"
            f"&from={from_currency}"
            f"&to={to_currency}"
            f"&amount={amount}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        _set_cached(cache_key, result)
        return result

    # method == "latest": fetch EUR-based rates and compute the conversion manually
    url = (
        f"https://data.fixer.io/api/latest"
        f"?access_key={access_key}"
        f"&base=EUR"
        f"&symbols={from_currency},{to_currency}"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        return data  # propagate API error verbatim

    rates = data.get("rates", {})
    if from_currency not in rates or to_currency not in rates:
        return {
            "success": False,
            "error": {"info": f"Missing rate for {from_currency} or {to_currency}"},
        }

    rate = rates[to_currency] / rates[from_currency]
    result = {
        "success": True,
        "query": {"from": from_currency, "to": to_currency, "amount": amount},
        "info": {
            "timestamp": data.get("timestamp"),
            "rate": rate,
        },
        "result": amount * rate,
    }
    _set_cached(cache_key, result)
    return result


if __name__ == '__main__':
    import json

    print("Testing: 25 GBP -> JPY (method=latest)")
    try:
        data = convert(amount=25, from_currency="GBP", to_currency="JPY", method="latest")
        print(json.dumps(data, indent=2))
    except RuntimeError as e:
        print(f"Config error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")