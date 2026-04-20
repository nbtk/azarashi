
import os
import re

index_path = r'd:\documents\azaraC\src\definition\_index.h'
def_dir = r'd:\documents\azaraC\src\definition'

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

includes = re.findall(r'#include "(.+?)"', content)
on_disk = os.listdir(def_dir)

missing = []
for inc in includes:
    if inc not in on_disk:
        missing.append(inc)

print(f"Total includes in _index.h: {len(includes)}")
print(f"Total files on disk: {len(on_disk)}")
print(f"Missing files: {len(missing)}")
for m in missing:
    print(f"  {m}")
