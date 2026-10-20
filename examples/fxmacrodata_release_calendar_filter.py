"""FXMacroData release-calendar filter for QSTrader examples.

QSTrader schedules portfolio construction by date. This helper preloads public
FXMacroData calendar events and exposes a date filter that can be checked before
creating signals, orders, or rebalance targets.
"""

from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
from math import isfinite
from typing import Any, Dict, Iterable, List, Set
from urllib.parse import urlencode
from urllib.request import urlopen


FXMD_CALENDAR_URL = "https://api.fxmacrodata.com/v1/calendar/{currency}"


def fetch_release_events(
    currency: str,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    params = urlencode({"start_date": start_date, "end_date": end_date})
    url = f"{FXMD_CALENDAR_URL.format(currency=currency.upper())}?{params}"

    with urlopen(url, timeout=20) as response:
        payload = json.load(response)

    events = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        raise ValueError("FXMacroData returned an unexpected calendar response")
    return events


def build_blackout_dates(
    events: Iterable[Dict[str, Any]],
    min_market_tier: int = 1,
    window_days: int = 0,
) -> Set[str]:
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 0:
        raise ValueError("window_days must be a non-negative integer")
    if isinstance(min_market_tier, bool) or not isinstance(min_market_tier, int) or min_market_tier < 1:
        raise ValueError("min_market_tier must be a positive integer")
    blackout_dates: Set[str] = set()

    for event in events:
        if event.get("release_date_confirmed") is not True:
            continue

        market_tier = event.get("market_tier")
        if isinstance(market_tier, bool):
            continue
        try:
            tier = float(market_tier)
        except (ValueError, TypeError, OverflowError):
            continue
        if not isfinite(tier) or not tier.is_integer() or tier < 1 or tier > min_market_tier:
            continue

        announcement_ts = event.get("announcement_datetime")
        if announcement_ts is None or isinstance(announcement_ts, bool):
            continue

        try:
            event_date = datetime.fromtimestamp(
                float(announcement_ts),
                tz=timezone.utc,
            ).date()
        except (ValueError, TypeError, OverflowError, OSError):
            continue
        for offset in range(-window_days, window_days + 1):
            blackout_dates.add((event_date + timedelta(days=offset)).isoformat())

    return blackout_dates


class MacroCalendarFilter:
    def __init__(self, blackout_dates: Set[str]) -> None:
        self.blackout_dates = blackout_dates

    @classmethod
    def from_fxmacrodata(cls, start_date: str, end_date: str) -> "MacroCalendarFilter":
        events = fetch_release_events("USD", start_date, end_date)
        return cls(build_blackout_dates(events, min_market_tier=1, window_days=0))

    def is_tradeable(self, trading_date: date) -> bool:
        return trading_date.isoformat() not in self.blackout_dates


# Example:
#
# macro_filter = MacroCalendarFilter.from_fxmacrodata("2026-07-01", "2026-07-31")
# if macro_filter.is_tradeable(timestamp.date()):
#     rebalance_portfolio()
