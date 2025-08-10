from __future__ import annotations
from pathlib import Path
from typing import List, Dict


def shallow_tree(root: Path) -> List[Dict]:
    items = []
    if not root.exists():
        return items
    for p in sorted(root.iterdir()):
        if p.name.startswith("."):
            continue
        st = p.stat()
        items.append(
            {
                "path": str(p.relative_to(root)),
                "is_dir": p.is_dir(),
                "size": 0 if p.is_dir() else st.st_size,
                "mtime": int(st.st_mtime),
            }
        )
    return items


