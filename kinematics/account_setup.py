"""Print the owner's single-use local setup link. Never share this link with students."""
import argparse
import json
from pathlib import Path

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    file=Path(__file__).resolve().parents[1]/'var/private/kinematics/admin-setup.json'
    if not file.exists():
        raise SystemExit('No pending administrator setup. Start the server first, or sign in to the existing admin account.')
    token=json.loads(file.read_text())['token']
    print(f'http://127.0.0.1:{args.port}/setup#token={token}')
