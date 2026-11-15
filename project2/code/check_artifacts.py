"""Check report figure formats, preview DPI, paths, and archived evidence hashes."""
import hashlib
import json
from pathlib import Path
import re

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT/'report'


def main():
    rows, failures = [], []
    for pdf in sorted((REPORT/'figures').glob('*.pdf')):
        reader = PdfReader(pdf)
        images = sum(len(page.images) for page in reader.pages)
        png = pdf.with_suffix('.png')
        dpi = Image.open(png).info.get('dpi', (0, 0)) if png.exists() else (0, 0)
        ok = images == 0 and min(dpi) >= 299.9 and not re.search(r'20\d{6}', pdf.stem)
        row = dict(file=str(pdf.relative_to(ROOT)), pages=len(reader.pages),
                   raster_images=images, preview_dpi=dpi, passed=ok,
                   sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
        rows.append(row)
        if not ok:
            failures.append(row['file'])
    for name in ['algorithm_section.tex', 'interface_pinn_section.tex']:
        text = (REPORT/name).read_text(encoding='utf-8')
        for asset in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
            if not (REPORT/asset).is_file() or Path(asset).suffix != '.pdf':
                failures.append('missing/non-PDF include: '+asset)
    base = REPORT/'support/interface_pinn'
    for rel, digest in json.loads((base/'source_hashes.json').read_text()).items():
        if hashlib.sha256((base/rel).read_bytes()).hexdigest() != digest:
            failures.append('archive hash mismatch: '+rel)
    trail = REPORT/'support/ai_log/transcript_excerpts.md'
    digest = hashlib.sha256(trail.read_bytes()).hexdigest()
    if digest not in (REPORT/'APPENDIX/AI_Theory_MeichenDing.tex').read_text(encoding='utf-8'):
        failures.append('AI audit hash mismatch')
    result = dict(passed=not failures, figures=rows, failures=failures,
                  note='Vector PDF DPI is resolution-independent; the 300 dpi check applies to PNG previews.')
    out = ROOT/'reviews/evidence/artifact_check.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
