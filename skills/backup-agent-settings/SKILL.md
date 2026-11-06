---
name: backup-agent-settings
description: Use when the user asks for a backup, copy, archive or export of Codex or Claude Code settings (.codex, .claude) - kopia zapasowa, backup ustawień, archiwizacja, eksport konfiguracji agentów, przeniesienie ustawień na inny komputer.
---

# Backup ustawień Codex i Claude Code

Tworzy jeden plik ZIP z `~/.codex` i `~/.claude` (Windows, Linux, macOS). Skrypt tylko czyta pliki źródłowe - niczego nie usuwa, nie modyfikuje i nie wysyła.

Domyślnie pomija historię rozmów (`sessions`, `projects`), cache, wygenerowane obrazy i pliki większe niż 50 MB - bez tego backup `.codex` waży kilkadziesiąt GB.

## Procedura

1. Uruchom skrypt leżący obok tego pliku, w `scripts/backup.py` (użyj katalogu bazowego skilla, nie zgaduj ścieżki):

```bash
python3 "<katalog-skilla>/scripts/backup.py"
```

Windows (PowerShell): `python "<katalog-skilla>\scripts\backup.py"`

2. Jeśli `python3` / `python` nie działa, spróbuj `py -3`. Jeśli wszystko zawiedzie, powiedz użytkownikowi, że potrzebny jest Python 3.8+.

3. Opcje - dodaj tylko na prośbę użytkownika:
   - `--output <plik.zip lub katalog>` - miejsce zapisu (domyślnie katalog domowy),
   - `--full` - wszystko, łącznie z historią rozmów i bez limitu rozmiaru (uprzedź, że może to być dziesiątki GB),
   - `--exclude <wzorzec>` - dodatkowe wykluczenie, np. `.codex/kdp` (można powtarzać),
   - `--max-file-mb <N>` - zmiana limitu rozmiaru pliku (`0` = bez limitu).

4. Po zakończeniu pokaż: pełną ścieżkę ZIP-a, rozmiar, liczbę spakowanych plików oraz to, co pominięto (wykluczenia, zbyt duże pliki, nieczytelne pliki, brakujące katalogi).

## Zasady bezpieczeństwa

- ZIP zawiera tokeny i dane logowania (np. `.credentials.json`). Nie wysyłaj go przez internet, nie wyświetlaj jego zawartości ani wartości kluczy.
- Skrypt nie nadpisuje istniejącego pliku i nie zostawia niedokończonych archiwów.
- Kod wyjścia `1` (brak katalogów, plik już istnieje, błąd zapisu) zgłoś użytkownikowi wprost, bez ponawiania w pętli.
