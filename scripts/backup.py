#!/usr/bin/env python3
"""Backup ustawień Codex i Claude Code do jednego pliku ZIP."""
import argparse
import datetime as dt
import fnmatch
import os
import sys
import zipfile
from pathlib import Path

# Domyślnie pomijane: historia rozmów, cache, wygenerowane obrazy i inne dane
# odtwarzalne. Wzorce dopasowywane są (fnmatch) do ścieżki w archiwum, np.
# ".codex/sessions". "--full" wyłącza tę listę i limit rozmiaru pliku.
DEFAULT_EXCLUDES = [
    ".codex/sessions",
    ".codex/archived_sessions",
    ".codex/generated_images",
    ".codex/packages",
    ".codex/.sandbox-bin",
    ".codex/.tmp",
    ".codex/cache",
    ".claude/projects",
    ".claude/shell-snapshots",
    "*/plugins/cache",
    "*/node_modules",
    "*/__pycache__",
]
DEFAULT_MAX_FILE_MB = 50


def human_size(size: int) -> str:
    value = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024


def is_excluded(archive_path: str, patterns) -> bool:
    return any(fnmatch.fnmatch(archive_path, pattern) for pattern in patterns)


def collect_files(source: Path, archive_root: str, patterns, max_bytes, stats):
    """Zwraca (ścieżka, nazwa w archiwum); zlicza pominięcia w `stats`."""

    def on_error(error):
        stats["unreadable"].append(f"{error.filename}: {error.strerror}")

    for current, dirs, files in os.walk(source, onerror=on_error):
        rel = Path(current).relative_to(source).as_posix()
        base = archive_root if rel == "." else f"{archive_root}/{rel}"

        kept = []
        for name in sorted(dirs):
            full = Path(current, name)
            if full.is_symlink():
                stats["symlinks"] += 1
            elif is_excluded(f"{base}/{name}", patterns):
                stats["excluded_dirs"] += 1
            else:
                kept.append(name)
        dirs[:] = kept

        for name in sorted(files):
            full = Path(current, name)
            archive_name = f"{base}/{name}"
            if full.is_symlink():
                stats["symlinks"] += 1
            elif is_excluded(archive_name, patterns):
                stats["excluded_files"] += 1
            else:
                try:
                    size = full.stat().st_size
                except OSError as error:
                    stats["unreadable"].append(f"{full}: {error.strerror}")
                    continue
                if max_bytes and size > max_bytes:
                    stats["too_large"].append(f"{archive_name} ({human_size(size)})")
                else:
                    yield full, archive_name


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # polskie znaki w starych konsolach Windows
        except (AttributeError, ValueError):
            pass

    parser = argparse.ArgumentParser(
        description="Backup ustawień Codex i Claude Code do pliku ZIP."
    )
    parser.add_argument(
        "--output",
        help="Ścieżka pliku ZIP (lub istniejącego katalogu). Domyślnie katalog domowy.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Spakuj wszystko: bez domyślnych wykluczeń i bez limitu rozmiaru pliku.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="WZORZEC",
        help="Dodatkowe wykluczenie, np. .codex/kdp lub '*/Anliza' (można powtarzać).",
    )
    parser.add_argument(
        "--max-file-mb",
        type=int,
        default=DEFAULT_MAX_FILE_MB,
        help=f"Pomijaj pliki większe niż N MB (domyślnie {DEFAULT_MAX_FILE_MB}, 0 = bez limitu).",
    )
    args = parser.parse_args()

    home = Path.home()
    sources = [(home / ".codex", ".codex"), (home / ".claude", ".claude")]
    existing = [(path, root) for path, root in sources if path.is_dir()]
    missing = [str(path) for path, _ in sources if not path.is_dir()]

    if not existing:
        print("BŁĄD: Nie znaleziono żadnego z katalogów:")
        for path in missing:
            print(f"  - {path}")
        return 1

    patterns = list(args.exclude) if args.full else DEFAULT_EXCLUDES + list(args.exclude)
    max_bytes = 0 if args.full else max(args.max_file_mb, 0) * 1024 * 1024

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    default_name = f"agent-settings-backup-{timestamp}.zip"
    if args.output:
        output = Path(args.output).expanduser()
        if output.is_dir():
            output = output / default_name
    else:
        output = home / default_name
    output = output.absolute()

    if output.exists():
        print(f"BŁĄD: Plik wynikowy już istnieje: {output}")
        return 1

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"BŁĄD: Nie można utworzyć katalogu docelowego: {error}")
        return 1

    stats = {
        "excluded_dirs": 0,
        "excluded_files": 0,
        "symlinks": 0,
        "too_large": [],
        "unreadable": [],
    }
    file_count = 0
    finished = False

    try:
        # "x" = nigdy nie nadpisuj; strict_timestamps=False = pliki sprzed 1980 nie psują backupu
        with zipfile.ZipFile(
            output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6, strict_timestamps=False
        ) as archive:
            for source, archive_root in existing:
                for file_path, archive_name in collect_files(
                    source, archive_root, patterns, max_bytes, stats
                ):
                    if file_path.absolute() == output:
                        continue  # nie pakuj archiwum do samego siebie
                    try:
                        archive.write(file_path, archive_name)
                        file_count += 1
                    except (OSError, ValueError) as error:
                        stats["unreadable"].append(f"{file_path}: {error}")
        finished = True
    except OSError as error:
        print(f"BŁĄD: Nie udało się utworzyć archiwum: {error}")
        return 1
    finally:
        if not finished and output.exists():
            output.unlink(missing_ok=True)  # żadnych niedokończonych ZIP-ów

    print(f"Utworzono backup: {output}")
    print(f"Rozmiar: {human_size(output.stat().st_size)}")
    print(f"Liczba spakowanych plików: {file_count}")

    if args.full:
        print("Tryb pełny: bez domyślnych wykluczeń.")
    else:
        print(
            f"Pominięto wg wykluczeń: {stats['excluded_dirs']} katalogów, "
            f"{stats['excluded_files']} plików (użyj --full, by spakować wszystko)."
        )
    if stats["too_large"]:
        print(f"Pominięto pliki większe niż {args.max_file_mb} MB ({len(stats['too_large'])}):")
        for item in stats["too_large"][:10]:
            print(f"  - {item}")
        if len(stats["too_large"]) > 10:
            print(f"  ... i {len(stats['too_large']) - 10} więcej")
    if stats["symlinks"]:
        print(f"Pominięto dowiązania symboliczne: {stats['symlinks']}")
    if stats["unreadable"]:
        print(f"UWAGA: Nie udało się odczytać ({len(stats['unreadable'])}):")
        for item in stats["unreadable"][:10]:
            print(f"  - {item}")
        if len(stats["unreadable"]) > 10:
            print(f"  ... i {len(stats['unreadable']) - 10} więcej")
    if missing:
        print("Pominięto nieistniejące katalogi:")
        for path in missing:
            print(f"  - {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
