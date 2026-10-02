#!/usr/bin/env bash
echo "======================================================="
echo "  LOST GOD 24/7 Telegram Bot Fleet Engine"
echo "======================================================="
echo ""
echo "[1/3] Installing Dependencies..."
pip3 install python-telegram-bot==21.6 httpx aiohttp
npm install

echo ""
echo "[2/3] Starting Server..."
echo "Open browser at: http://localhost:3000"
npm start
