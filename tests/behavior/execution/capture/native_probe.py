"""Offline candidate adapter fixture. This is not a real mobile integration."""
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['manual-save', 'capture'])
args = parser.parse_args()
if args.operation == 'manual-save':
    print(json.dumps({'status': 'saved', 'readback': True}))
else:
    print(json.dumps({'status': 'blocked', 'reason': 'target device unavailable',
                      'installed_version': None, 'automatic_trigger_verified': False}))
    raise SystemExit(3)
