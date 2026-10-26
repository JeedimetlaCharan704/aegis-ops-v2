"""Root Flask entrypoint for AegisOps (compatible with Vercel and local runs)."""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from web_dashboard.app import app

application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
