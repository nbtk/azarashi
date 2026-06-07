# azaraC - scripts/strategy.py
# Lookup strategy selector (shared by gen_definitions.py).

def key_type(keys: list) -> str:
    mx = max(keys) if keys else 0
    if mx > 0xFFFFFFFF: return "uint64_t"
    if mx > 0xFFFF:     return "uint32_t"
    if mx > 0xFF:       return "uint16_t"
    return "uint8_t"

def choose(keys: list) -> str:
    """
    switch        : n <= 10
    array         : fill_ratio >= 0.6 AND max key <= 0xFFFF
    binary_search : otherwise (sparse, large keys)
    """
    if not keys: return "switch"
    n  = len(keys)
    mn, mx = min(keys), max(keys)
    span = mx - mn + 1
    fill = n / span if span > 0 else 1.0
    if mx > 0xFFFF:   return "binary_search"
    if n <= 10:       return "switch"
    if fill >= 0.6:   return "array"
    return "binary_search"
