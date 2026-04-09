#!/usr/bin/env python3
"""
Run this script to list all text/chat models available in your AWS Bedrock account.
It shows the exact model ID to use in config.py.

Usage:
    cd backend
    source venv/bin/activate
    python check_models.py
"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
profile = os.getenv('AWS_PROFILE')

session = boto3.Session(profile_name=profile) if profile else boto3.Session()
client = session.client('bedrock', region_name=region)

print(f"\nRegion : {region}")
print(f"Profile: {profile or 'default'}\n")

resp = client.list_foundation_models(byOutputModality='TEXT')
models = sorted(resp['modelSummaries'], key=lambda m: m['modelId'])

providers = {}
for m in models:
    if m.get('responseStreamingSupported') is False:
        continue                        # skip non-streaming models
    provider = m.get('providerName', 'Unknown')
    providers.setdefault(provider, []).append(m)

for provider, items in providers.items():
    print(f"── {provider} ──────────────────────────────────────")
    for m in items:
        status = m.get('modelLifecycle', {}).get('status', '')
        stream = '✓ stream' if m.get('responseStreamingSupported') else '✗ stream'
        print(f"  {stream}  {m['modelId']:<60}  {m.get('modelName','')}")
    print()

print("Copy the modelId values above into backend/config.py MODELS dict.")
