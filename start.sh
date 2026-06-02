#!/usr/bin/env sh
exec gunicorn backend.app:app --bind 0.0.0.0:${PORT:-5000}
