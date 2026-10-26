"""Vercel Serverless Entrypoint for AegisOps Web Dashboard."""

import sys
import os

# Add root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from web_dashboard.app import app

# Vercel WSGI entry point
application = app

