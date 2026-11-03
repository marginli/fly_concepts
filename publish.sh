#!/bin/bash
# 重建網頁並推上 GitHub。用法：./publish.sh "說明"
set -e
cd "$(dirname "$0")"
# 先抓 GitHub 上的最新版（網頁上可能刪過條目），免得把刪掉的推回去
git pull --rebase --autostash -q origin main
python3 build.py
git add -A
git commit -m "${1:-update}" || echo "（沒有變更）"
git push origin main
echo "網址：https://marginli.github.io/fly_concepts/"
