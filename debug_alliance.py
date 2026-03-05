#!/usr/bin/env python3
"""Debug: inspect u[] array and m.m[] array in alliance_data.bin"""
import sys, msgpack

def show(obj, depth=0, max_depth=3):
    ind = "  " * depth
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for k, v in list(obj.items())[:15]:
            if isinstance(v, (dict, list)):
                print(f"{ind}{k!r}: ({type(v).__name__}, {len(v)} items)")
                show(v, depth+1, max_depth)
            elif isinstance(v, str) and len(v) > 50:
                print(f"{ind}{k!r}: str({len(v)} chars)")
            else:
                print(f"{ind}{k!r}: {v!r}")
        if len(obj) > 15:
            print(f"{ind}... +{len(obj)-15} more keys")
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:2]):
            print(f"{ind}[{i}]:")
            show(item, depth+1, max_depth)
        if len(obj) > 2:
            print(f"{ind}... +{len(obj)-2} more")

fpath = sys.argv[1] if len(sys.argv) > 1 else "siege_data/alliance_data.bin"
with open(fpath, "rb") as f:
    data = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)

# Show u[] array structure (the 30-item list)
print("=== data['u'][0] (first player profile) ===")
if 'u' in data and isinstance(data['u'], list) and len(data['u']) > 0:
    show(data['u'][0], max_depth=2)
    print(f"\n=== data['u'][1] (second player profile) ===")
    if len(data['u']) > 1:
        show(data['u'][1], max_depth=2)

# Also check d.m.m structure
print(f"\n=== data['d']['m']['m'][0] (first member entry) ===")
try:
    show(data['d']['m']['m'][0], max_depth=2)
except:
    print("Not found at data.d.m.m")

print("\nDone.")
