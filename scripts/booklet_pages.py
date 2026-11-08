"""Contact sheets of the sewing booklet for the visual check before delivery (SKILL.md step 6).

    python scripts/booklet_pages.py out/sewing_instructions.pdf [--out out/booklet_check] [--per 4]

Renders every page of the illustrated booklet (the pages before the reference pages) and
puts them side by side, ``--per`` pages per sheet, with the page number under each page.
Look at every sheet: the automatic checks (``booklet_qa``) cannot judge whether a picture
makes sense to a sewist.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile


def booklet_pages(pdf: str) -> int:
    """Number of booklet pages: everything before the reference part (its first heading)."""
    from pypdf import PdfReader
    pages = PdfReader(pdf).pages
    for i, pg in enumerate(pages):
        text = (pg.extract_text() or "")[:400]
        if i > 2 and any(k in text for k in ("Printing", "Drucken", "Files", "Dateien")):
            return i
    return len(pages)


def contact_sheets(pdf: str, out_dir: str, per: int = 4, dpi: int = 60) -> list[str]:
    from PIL import Image, ImageDraw
    if not shutil.which("pdftoppm"):
        raise SystemExit("pdftoppm (poppler-utils) is needed to render the pages")
    os.makedirs(out_dir, exist_ok=True)
    n = booklet_pages(pdf)
    sheets = []
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", "1", "-l", str(n), pdf,
                        os.path.join(tmp, "p")], check=True)
        files = sorted(os.listdir(tmp))
        for s in range(0, len(files), per):
            ims = [Image.open(os.path.join(tmp, f)).convert("RGB") for f in files[s:s + per]]
            w, h = ims[0].size
            sheet = Image.new("RGB", (w * len(ims), h + 18), "white")
            d = ImageDraw.Draw(sheet)
            for k, im in enumerate(ims):
                sheet.paste(im, (k * w, 0))
                d.rectangle([k * w, 0, (k + 1) * w - 1, h - 1], outline="#bbbbbb")
                d.text((k * w + w // 2 - 10, h + 3), f"p. {s + k + 1}", fill="black")
            path = os.path.join(out_dir, f"booklet_pages_{s + 1:02d}-{s + len(ims):02d}.png")
            sheet.save(path)
            sheets.append(path)
    return sheets


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf")
    ap.add_argument("--out", default=None)
    ap.add_argument("--per", type=int, default=4)
    a = ap.parse_args(argv)
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.pdf)), "booklet_check")
    for p in contact_sheets(a.pdf, out, a.per):
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
