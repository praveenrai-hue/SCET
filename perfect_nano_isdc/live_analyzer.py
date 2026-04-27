from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict

from upstox_client import UpstoxClient, UpstoxConfig


BANKNIFTY_INDEX_KEY = "NSE_INDEX|Nifty Bank"
LOT_SIZE = 15
RISK_PCT = 0.03


@dataclass
class RiskBudget:
    capital: float
    risk_rupees: float
    max_debit_per_share: float


def calculate_risk_budget(capital: float) -> RiskBudget:
    risk_rupees = capital * RISK_PCT
    max_debit_per_share = risk_rupees / LOT_SIZE
    return RiskBudget(capital=capital, risk_rupees=risk_rupees, max_debit_per_share=max_debit_per_share)


def is_safe_entry_window(now_ist: dt.datetime) -> bool:
    # Tuesday=1, Wednesday=2 in Python's weekday numbering.
    return now_ist.weekday() in (1, 2) and (now_ist.hour < 14 or (now_ist.hour == 14 and now_ist.minute == 0))


def summarize_market_snapshot(snapshot: Dict[str, Any]) -> str:
    data = snapshot.get("data", {})
    row = data.get(BANKNIFTY_INDEX_KEY, {}) if isinstance(data, dict) else {}
    ltp = row.get("last_price") or row.get("ltp")
    ts = row.get("timestamp")
    return f"BANKNIFTY LTP: {ltp} | timestamp: {ts}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Perfect Nano ISDC v2.0 live data bootstrap via Upstox")
    parser.add_argument("--capital", type=float, required=True, help="Account capital in INR (5000-10000).")
    parser.add_argument("--expiry", type=str, required=True, help="Expiry date in YYYY-MM-DD format.")
    args = parser.parse_args()

    if args.capital < 5000 or args.capital > 10000:
        raise ValueError("capital must be within ₹5,000 to ₹10,000 for Nano mode.")

    config = UpstoxConfig.from_env()
    client = UpstoxClient(config)

    budget = calculate_risk_budget(args.capital)
    ltp_payload = client.get_ltp(BANKNIFTY_INDEX_KEY)
    chain_payload = client.get_option_chain(BANKNIFTY_INDEX_KEY, args.expiry)

    now_ist = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    print("=== Perfect Nano ISDC v2.0 (Upstox Live) ===")
    print(summarize_market_snapshot(ltp_payload))
    print(f"Capital: ₹{budget.capital:.2f}")
    print(f"Max risk/trade (3%): ₹{budget.risk_rupees:.2f}")
    print(f"Max net debit/share: ₹{budget.max_debit_per_share:.2f}")
    print(f"Safe entry window now: {'YES' if is_safe_entry_window(now_ist) else 'NO'}")

    chain_rows = chain_payload.get("data", [])
    row_count = len(chain_rows) if isinstance(chain_rows, list) else 0
    print(f"Option-chain rows fetched for {args.expiry}: {row_count}")
    print("Next step: connect this chain snapshot to your 6-pillar validator + spread picker logic.")


if __name__ == "__main__":
    main()
