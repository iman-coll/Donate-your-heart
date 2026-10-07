"""Build a copy of the app with the self-test appended, then report the result."""
import re, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "tools" / "site"
SITE.mkdir(parents=True, exist_ok=True)

src = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
inject = '\n<script src="selftest.js"></script>\n</body>'
if "</body>" not in src:
    sys.exit("no </body> in index.html")
(SITE / "index.html").write_text(src.replace("</body>", inject, 1), encoding="utf-8")
shutil.copy(ROOT / "tools" / "selftest.js", SITE / "selftest.js")
print("built", SITE / "index.html")

# report mode: pull the results block out of a dumped DOM
if len(sys.argv) > 1 and sys.argv[1] == "report":
    dump = (ROOT / "tools" / "dump.html").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"@@@BEGIN@@@(.*?)@@@END@@@", dump, re.S)
    if not m:
        print("!! no results block in the dump — the app probably threw before the test ran")
        errs = re.findall(r"(Uncaught[^<\n]{0,200})", dump)
        for e in errs[:10]:
            print("  ", e)
        sys.exit(1)
    print(m.group(1).strip())
    sys.exit(1 if "FAIL ::" in m.group(1) else 0)
