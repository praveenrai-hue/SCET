# Perfect Nano ISDC v2.0 — Upstox Live Data Integration

This repository now includes a minimal live-data integration layer for your Perfect Nano ISDC v2.0 workflow using the Upstox API.

## What was added

- `perfect_nano_isdc/upstox_client.py`
  - Authenticated Upstox HTTP client.
  - Helpers for LTP, intraday OHLC, and option-chain fetch.
- `perfect_nano_isdc/live_analyzer.py`
  - CLI bootstrap to compute Nano risk budget and pull live BANKNIFTY + option chain data.
  - Safe entry window check (Tue/Wed, up to 2:00 PM IST).
- `.env.example` with `UPSTOX_ACCESS_TOKEN` placeholder.

## Setup

```bash
cd /workspace/SCET
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# export token to shell (or load via your preferred env manager)
export UPSTOX_ACCESS_TOKEN="<your_token>"
```

## Run live analysis bootstrap

```bash
cd /workspace/SCET/perfect_nano_isdc
python3 live_analyzer.py --capital 8000 --expiry 2026-04-30
```

## Notes

- This implementation safely adds live market connectivity and budget math.
- Your full 18/18 pillar evaluation (trend/OB/OTE/RSI/ADX/volume/orderflow/news filters) should now be implemented against these live payloads in the next step.
