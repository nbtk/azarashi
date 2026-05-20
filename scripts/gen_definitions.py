#!/usr/bin/env python3
# azaraC - scripts/gen_definitions.py
# Generates src/definition/*.h from azarashi (installed in current env).
#
# Usage:
#   pip install azarashi==<version>
#   python scripts/gen_definitions.py [--out-dir src/definition]

import argparse, importlib, os, pkgutil, sys
from strategy import choose, key_type

BASE_MOD = "azarashi.qzss_dcr_lib.definition"

def get_azarashi_version():
    try:
        from importlib.metadata import version
        return version("azarashi")
    except Exception:
        return "unknown"

def find_def_path():
    import azarashi.qzss_dcr_lib.definition as d
    return os.path.dirname(d.__file__)

def escape(s):
    return (str(s).replace("\\", "\\\\")
                  .replace('"', '\\"')
                  .replace("\n", "\\n")
                  .replace("\r", ""))

def emit_switch(varname, entries, guard, kt):
    lines = [f"[[nodiscard]] inline constexpr std::optional<std::string_view> {varname}_lookup({kt} id) {{",
             "    switch (id) {"]
    for k, v in sorted(entries.items()):
        lines.append(f'        case {k}: return "{escape(v)}";')
    lines += ['        default: return std::nullopt;', "    }", "}"]
    return "\n".join(lines)

def emit_array(varname, entries, guard, kt):
    keys = sorted(entries.keys())
    base, top = keys[0], keys[-1]
    table = [entries.get(i) for i in range(base, top + 1)]
    rows = ",\n    ".join(
        f'"{escape(v)}"' if v is not None else "std::nullopt" for v in table)
    return "\n".join([
        f"inline constexpr std::optional<std::string_view> {guard}_TABLE[] = {{",
        f"    {rows}", "};",
        f"inline constexpr {kt} {guard}_BASE = {base};",
        f"inline constexpr {kt} {guard}_SIZE = {top - base + 1};",
        f"[[nodiscard]] inline constexpr std::optional<std::string_view> {varname}_lookup({kt} id) {{",
        f"    if (id < {guard}_BASE || id >= {guard}_BASE + {guard}_SIZE) return std::nullopt;",
        f"    return {guard}_TABLE[id - {guard}_BASE];", "}",
    ])

def emit_bsearch(varname, entries, guard, kt):
    keys = sorted(entries.keys())
    n = len(keys)
    idx_type = "uint8_t" if n <= 255 else ("uint16_t" if n <= 65535 else "uint32_t")
    rows = "\n".join(f'    {{{k}u, "{escape(entries[k])}"}},\n' for k in keys)
    return "\n".join([
        f"struct {guard}_Entry {{ {kt} id; std::string_view label; }};",
        f"inline constexpr {guard}_Entry {guard}_TABLE[] = {{",
        rows + "};",
        f"[[nodiscard]] inline constexpr std::optional<std::string_view> {varname}_lookup({kt} id) {{",
        f"    {idx_type} lo = 0, hi = {n};",
        "    while (lo < hi) {",
        f"        {idx_type} mid = static_cast<{idx_type}>(lo + (hi - lo) / 2);",
        f"        if ({guard}_TABLE[mid].id == id) return {guard}_TABLE[mid].label;",
        f"        if ({guard}_TABLE[mid].id < id) lo = mid + 1;",
        "        else hi = mid;",
        "    }",
        "    return std::nullopt;", "}",
    ])

def build_header(modname, varname, entries, ver):
    keys = [k for k in entries.keys() if isinstance(k, int)]
    if not keys: return None
    int_entries = {k: entries[k] for k in keys}
    guard = varname.upper()
    kt    = key_type(keys)
    strat = choose(keys)
    if   strat == "switch": body = emit_switch(varname, int_entries, guard, kt)
    elif strat == "array":  body = emit_array(varname, int_entries, guard, kt)
    else:                   body = emit_bsearch(varname, int_entries, guard, kt)
    return (
        f"#pragma once\n"
        f"// AUTO-GENERATED from azarashi {ver} with CI-CD\n"
        f"// Source module : {modname}\n"
        f"// Variable      : {varname}\n"
        f"// Entries       : {len(keys)}\n"
        f"// Strategy      : {strat}\n\n"
        f"#include <cstdint>\n"
        f"#include <optional>\n"
        f"#include <string_view>\n\n"
        f"namespace azaraC {{\nnamespace def {{\n\n"
        f"{body}\n\n"
        f"}} // namespace def\n}} // namespace azaraC\n"
    )

def run(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    base_path = find_def_path()
    ver = get_azarashi_version()
    generated = []
    for _, modname, _ in pkgutil.iter_modules([base_path]):
        try:
            mod = importlib.import_module(f"{BASE_MOD}.{modname}")
        except Exception as e:
            print(f"[WARN] skip {modname}: {e}", file=sys.stderr)
            continue
        for attr in dir(mod):
            if attr.startswith("_"): continue
            obj = getattr(mod, attr)
            if not isinstance(obj, dict): continue
            hdr = build_header(modname, attr, obj, ver)
            if hdr is None: continue
            with open(os.path.join(out_dir, f"{attr}.h"), "w", encoding="utf-8") as f:
                f.write(hdr)
            generated.append(attr)
    # _index.h
    idx = (
        "#pragma once\n"
        f"// AUTO-GENERATED from azarashi {ver} — do not edit\n"
        f"// {len(generated)} definition headers\n\n"
        + "\n".join(f'#include "{a}.h"' for a in sorted(generated))
        + "\n"
        + '#include "ublox_qzss_svid_prn_map.h"\n'
        + '#include "qzss_dcx_camf_a3_provider_identifier.h"\n'
    )
    with open(os.path.join(out_dir, "_index.h"), "w", encoding="utf-8") as f:
        f.write(idx)
    # version marker
    with open(".azarashi-version", "w") as f:
        f.write(ver + "\n")
    print(f"Generated {len(generated)} headers + _index.h  (azarashi {ver})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="src/definition")
    args = parser.parse_args()
    run(args.out_dir)
