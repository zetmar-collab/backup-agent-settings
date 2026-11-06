# Backup ustawień Codex i Claude Code

Ten skill tworzy kopię zapasową ustawień użytkownika z katalogów:

- `~/.codex`
- `~/.claude`

Wynikiem jest jeden plik ZIP z zachowaną strukturą katalogów. Skrypt działa na Windows, Linux i macOS.

## Zawartość

```text
backup-agent-settings/
├── SKILL.md
├── README.md
└── scripts/
    └── backup.py
```

## Wymagania

- Python 3.8 lub nowszy
- Claude Code lub Codex z obsługą skills
- Dostęp do katalogu domowego użytkownika

## Instalacja

### Claude Code

Rozpakuj archiwum i umieść cały katalog `backup-agent-settings` w:

```text
~/.claude/skills/backup-agent-settings/
```

Po instalacji struktura powinna wyglądać tak:

```text
~/.claude/skills/backup-agent-settings/
├── SKILL.md
├── README.md
└── scripts/
    └── backup.py
```

### Codex

Rozpakuj archiwum i umieść cały katalog `backup-agent-settings` w:

```text
~/.codex/skills/backup-agent-settings/
```

Po instalacji struktura powinna wyglądać tak:

```text
~/.codex/skills/backup-agent-settings/
├── SKILL.md
├── README.md
└── scripts/
    └── backup.py
```

## Uruchamianie przez agenta

W Claude Code lub Codex wpisz:

```text
Zrób backup ustawień Codex i Claude Code
```

Możesz też użyć bardziej konkretnego polecenia:

```text
Użyj skillu backup-agent-settings i utwórz kopię zapasową ustawień
```

Agent powinien odnaleźć skill po nazwie i opisie w pliku `SKILL.md`, a następnie uruchomić `scripts/backup.py`.

## Uruchamianie ręczne

### Linux i macOS

```bash
python3 ~/.claude/skills/backup-agent-settings/scripts/backup.py
```

Dla instalacji w Codex:

```bash
python3 ~/.codex/skills/backup-agent-settings/scripts/backup.py
```

### Windows — PowerShell

```powershell
python "$HOME\.claude\skills\backup-agent-settings\scripts\backup.py"
```

Dla instalacji w Codex:

```powershell
python "$HOME\.codex\skills\backup-agent-settings\scripts\backup.py"
```

### Windows — CMD

```bat
python "%USERPROFILE%\.claude\skills\backup-agent-settings\scripts\backup.py"
```

Dla instalacji w Codex:

```bat
python "%USERPROFILE%\.codex\skills\backup-agent-settings\scripts\backup.py"
```

## Własna ścieżka ZIP-a

Możesz wskazać miejsce i nazwę pliku wynikowego:

### Linux i macOS

```bash
python3 ~/.claude/skills/backup-agent-settings/scripts/backup.py --output ~/Desktop/agent-backup.zip
```

### Windows PowerShell

```powershell
python "$HOME\.claude\skills\backup-agent-settings\scripts\backup.py" --output "$HOME\Desktop\agent-backup.zip"
```

### Windows CMD

```bat
python "%USERPROFILE%\.claude\skills\backup-agent-settings\scripts\backup.py" --output "%USERPROFILE%\Desktop\agent-backup.zip"
```

## Co trafia do backupu

Domyślnie skrypt pomija dane duże i odtwarzalne, bo samo `~/.codex` potrafi ważyć kilkadziesiąt GB:

- historię rozmów: `.codex/sessions`, `.codex/archived_sessions`, `.claude/projects`,
- cache i dane tymczasowe: `.codex/cache`, `.codex/.tmp`, `.codex/packages`, `.codex/.sandbox-bin`, `*/plugins/cache`, `node_modules`, `__pycache__`,
- `.codex/generated_images`,
- pojedyncze pliki większe niż 50 MB (np. bazy `*.sqlite` z historią),
- dowiązania symboliczne.

Opcje:

| Opcja | Działanie |
|-------|-----------|
| `--full` | pakuje wszystko, bez wykluczeń i bez limitu rozmiaru |
| `--exclude WZORZEC` | dodatkowe wykluczenie, np. `--exclude .codex/kdp` (można powtarzać) |
| `--max-file-mb N` | zmienia limit rozmiaru pliku (`0` = bez limitu) |
| `--output ŚCIEŻKA` | plik ZIP lub istniejący katalog docelowy |

## Wynik

Domyślnie skrypt tworzy plik w katalogu domowym:

```text
agent-settings-backup-YYYYMMDD-HHMMSS.zip
```

Przykład:

```text
agent-settings-backup-20261106-184500.zip
```

Po zakończeniu skrypt wyświetli:

- ścieżkę utworzonego ZIP-a,
- rozmiar archiwum,
- liczbę spakowanych plików,
- podsumowanie pominiętych elementów (wykluczenia, zbyt duże pliki, nieczytelne pliki, nieistniejące katalogi).

## Bezpieczeństwo

Katalogi `.codex` i `.claude` mogą zawierać tokeny API, klucze, historię rozmów oraz dane logowania. Nie wysyłaj utworzonego ZIP-a przez internet i przechowuj go wyłącznie lokalnie albo w zaszyfrowanym magazynie.

Skrypt:

- nie usuwa i nie modyfikuje plików źródłowych,
- nie nadpisuje istniejącego pliku ZIP,
- pomija pliki niedostępne (brak uprawnień, plik zablokowany przez inny program) i wypisuje je w podsumowaniu,
- usuwa niedokończony ZIP, jeśli zapis się nie powiedzie,
- nie wysyła danych przez sieć.
