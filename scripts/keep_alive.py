#!/usr/bin/env python3
"""
SoloMentor Render Keep-Alive Script
Pings your Render backend /health endpoint every 8-10 minutes
to prevent the free-tier service from spinning down / going to sleep.
"""

import sys
import time
import os
import urllib.request
import urllib.error
from datetime import datetime

# Default target URL (can be overridden via CLI argument or env var)
DEFAULT_URL = os.environ.get("RENDER_BACKEND_URL", "https://your-app-name.onrender.com/health")
PING_INTERVAL_SECONDS = 600  # 10 minutes (Render sleeps after 15 minutes)


def ping(target_url: str) -> bool:
    # Ensure URL ends with /health
    if not target_url.endswith("/health"):
        target_url = target_url.rstrip("/") + "/health"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "SoloMentor-KeepAlive/1.0"},
        )
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=30) as response:
            duration_ms = round((time.time() - start_time) * 1000)
            status = response.getcode()
            print(f"[{timestamp}] SUCCESS -> {target_url} (HTTP {status}) in {duration_ms}ms")
            return True
    except urllib.error.HTTPError as e:
        print(f"[{timestamp}] HTTP ERROR -> {target_url} (HTTP {e.code})")
        return False
    except urllib.error.URLError as e:
        print(f"[{timestamp}] CONNECTION ERROR -> {target_url}: {e.reason}")
        return False
    except Exception as e:
        print(f"[{timestamp}] UNEXPECTED ERROR -> {target_url}: {str(e)}")
        return False


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    if "your-app-name" in target:
        print("=" * 65)
        print("⚠️  ATTENTION: Replace with your actual Render or Proxy URL!")
        print("Example:")
        print("  python scripts/keep_alive.py https://solomentor.onrender.com/health")
        print("  or")
        print("  python scripts/keep_alive.py https://solomentor-proxy.workers.dev/health")
        print("=" * 65)
        sys.exit(1)

    print("=" * 65)
    print(f"🚀 SoloMentor Keep-Alive Monitor Active")
    print(f"📡 Target:   {target}")
    print(f"⏱️  Interval: Every {PING_INTERVAL_SECONDS // 60} minutes")
    print(f"Press CTRL+C to stop.")
    print("=" * 65)

    # Initial ping
    ping(target)

    while True:
        try:
            time.sleep(PING_INTERVAL_SECONDS)
            ping(target)
        except KeyboardInterrupt:
            print("\n🛑 Keep-alive monitor stopped.")
            break


if __name__ == "__main__":
    main()

