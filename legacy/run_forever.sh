#!/bin/bash

while true; do
    cd "$(dirname "$0")"
    python3 auto_draft_reply.py
    sleep 60
done
