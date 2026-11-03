#!/bin/bash
# 刪除條目並推上 GitHub。用法：./remove_entry.sh <條目編號>
set -e
cd "$(dirname "$0")"
[ -d "entries/$1" ] || { echo "找不到條目 $1"; ls entries; exit 1; }
git rm -rq "entries/$1"
rm -rf "entries/$1"
./publish.sh "remove $1"
