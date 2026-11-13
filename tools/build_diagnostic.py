"""Build the Life Journal diagnostic .ts4script with the selected Python."""
import argparse
import py_compile
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile


SOURCES = (
    "life_journal_probe.py",
    "prototypes/zone_session.py",
    "prototypes/json_journal_store.py",
    "prototypes/journal_entry_log.py",
)


def build(source_root, output):
    with TemporaryDirectory() as directory:
        scratch = Path(directory)
        init = scratch / "__init__.py"
        init.write_text("", encoding="utf-8")
        sources = [(name, source_root / name) for name in SOURCES]
        sources.append(("prototypes/__init__.py", init))
        with ZipFile(str(scratch / "diagnostic.zip"), "w", ZIP_DEFLATED) as archive:
            for name, source in sources:
                bytecode = scratch / "module.pyc"
                py_compile.compile(str(source), str(bytecode), dfile=name, doraise=True)
                archive.write(str(bytecode), name + "c")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes((scratch / "diagnostic.zip").read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", required=True, help="Target game Python major.minor")
    parser.add_argument("--output", type=Path, default=Path("dist/LifeJournalDiagnostic.ts4script"))
    args = parser.parse_args()
    actual = "{}.{}".format(*sys.version_info[:2])
    if args.python != actual:
        parser.error("Requested Python {}, but this interpreter is {}".format(args.python, actual))
    if args.output.suffix != ".ts4script":
        parser.error("--output must end with .ts4script")
    build(Path(__file__).resolve().parents[1], args.output)
    print("Built {} with Python {}".format(args.output, actual))


if __name__ == "__main__":
    main()
