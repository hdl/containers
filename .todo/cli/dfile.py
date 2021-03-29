from pathlib import Path

# https://github.com/asottile/dockerfile
import dockerfile

ROOT = Path(__file__).resolve().parent

print(dockerfile.all_cmds())

for item in dockerfile.parse_file(str(ROOT.parent.parent / 'debian-buster' / 'nextpnr.dockerfile')):
    print('·', item.cmd)
