#!/usr/bin/env python3
"""
Debug script: Inspect the structure of a .bin building file.
Usage: python debug_bin.py siege_data/building_XXXXXX_001.bin
"""
import sys
import msgpack

def show_structure(obj, depth=0, max_depth=6, path="root"):
    """Print the structure of the decoded data, showing types and keys."""
    indent = "  " * depth
    
    if depth > max_depth:
        print(f"{indent}... (max depth)")
        return
    
    if isinstance(obj, dict):
        print(f"{indent}{path}: dict ({len(obj)} keys)")
        for k, v in list(obj.items())[:30]:  # Limit keys shown
            key_repr = repr(k)
            if isinstance(v, (dict, list)):
                show_structure(v, depth + 1, max_depth, path=f"[{key_repr}]")
            elif isinstance(v, bool):
                print(f"{indent}  [{key_repr}]: bool = {v}")
            elif isinstance(v, (int, float)):
                print(f"{indent}  [{key_repr}]: {type(v).__name__} = {v}")
            elif isinstance(v, str):
                val = v[:50] + "..." if len(v) > 50 else v
                print(f"{indent}  [{key_repr}]: str = {val!r}")
            elif isinstance(v, bytes):
                print(f"{indent}  [{key_repr}]: bytes ({len(v)} bytes)")
            elif v is None:
                print(f"{indent}  [{key_repr}]: None")
            else:
                print(f"{indent}  [{key_repr}]: {type(v).__name__}")
    
    elif isinstance(obj, list):
        print(f"{indent}{path}: list ({len(obj)} items)")
        for i, item in enumerate(obj[:5]):  # Show first 5
            show_structure(item, depth + 1, max_depth, path=f"[{i}]")
        if len(obj) > 5:
            print(f"{indent}  ... and {len(obj) - 5} more items")


def find_attack_candidates(obj, path="root", depth=0, max_depth=15):
    """Find dicts that might be attack entries (have 'a'/'w' or similar)."""
    if depth > max_depth:
        return
    
    if isinstance(obj, dict):
        keys = set(obj.keys())
        # Look for dicts with both 'a' (or b'a') and 'w' (or b'w')
        key_strs = set()
        for k in keys:
            if isinstance(k, bytes):
                key_strs.add(k.decode('utf-8', errors='replace'))
            elif isinstance(k, str):
                key_strs.add(k)
        
        if 'a' in key_strs and 'w' in key_strs:
            w_key = 'w' if 'w' in keys else b'w'
            a_key = 'a' if 'a' in keys else b'a'
            w_val = obj.get(w_key)
            a_val = obj.get(a_key)
            
            a_has_i = False
            if isinstance(a_val, dict):
                a_keys = set()
                for k in a_val.keys():
                    if isinstance(k, bytes):
                        a_keys.add(k.decode('utf-8', errors='replace'))
                    elif isinstance(k, str):
                        a_keys.add(k)
                a_has_i = 'i' in a_keys
            
            if a_has_i:
                i_key = 'i' if 'i' in a_val else b'i'
                print(f"\n  ATTACK CANDIDATE at {path}:")
                print(f"    w = {w_val!r} (type: {type(w_val).__name__})")
                print(f"    a.i = {a_val.get(i_key, a_val.get(b'i', '?'))!r}")
                print(f"    Key types: {[type(k).__name__ for k in list(obj.keys())[:5]]}")
                return  # Found one, don't recurse deeper
        
        for k, v in obj.items():
            k_str = k.decode('utf-8', errors='replace') if isinstance(k, bytes) else str(k)
            find_attack_candidates(v, f"{path}.{k_str}", depth + 1, max_depth)
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:20]):
            find_attack_candidates(item, f"{path}[{i}]", depth + 1, max_depth)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_bin.py <path_to_bin_file>")
        sys.exit(1)
    
    fpath = sys.argv[1]
    with open(fpath, "rb") as f:
        data = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)
    
    print("=" * 60)
    print(f"  FILE: {fpath}")
    print(f"  Top-level type: {type(data).__name__}")
    print("=" * 60)
    print()
    
    print("STRUCTURE (first few levels):")
    show_structure(data, max_depth=4)
    
    print()
    print("=" * 60)
    print("SEARCHING FOR ATTACK ENTRIES...")
    print("=" * 60)
    find_attack_candidates(data)
    
    print()
    print("Done.")
