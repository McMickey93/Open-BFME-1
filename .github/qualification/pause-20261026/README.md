# McMickey93 — gesicherter Pausenstand vom 26.10.2026

Die Mitarbeit ist pausiert. Nach der Pausenanweisung wurde keine neue Funktion oder C++-Implementierung begonnen. Elf Abschlusscommits sichern die bereits vorhandenen Versuche, bessere Banken, native Messungen und konkrete Blocker. Alle normalen Commit-Hooks sowie der abschließende Pre-Push-Hook liefen erfolgreich.

Dieser Zweig enthält ausschließlich das Git-Bündel und diese Beschreibung. Er ist ein Archiv und verändert keinen Spielcode. Die elf enthaltenen Commits sind noch nicht in den offiziellen Hauptzweig aufgenommen.

## Unveränderlicher Prüfstand

| Merkmal | Wert |
| --- | --- |
| Basis im offiziellen BFME-1-Projekt | `7c1af3127d2e0b85ad028605e61b916b98e9dbba` |
| Abschlusscommit im Bündel | `7212b0d0398ca5e930b91cf096ff823ff24f868f` |
| Enthaltene Abschlusscommits | 11 |
| Bündel | [banked-attempts.bundle](./banked-attempts.bundle) |
| Bündelgröße | 76472 Bytes |
| SHA256 | `1e439a255fc7b3a25ad560b5c39c24b462e47bac819e10db755656021714e8ab` |
| Neue C++-Exact-Bytes aus diesen Arbeiten | **0** |

`git bundle verify` war erfolgreich. Die Abschlussprüfung `python3 tools/progress.py origin/master` ergab für BFME 1 C++ exact 7.604.426 Bytes und Delta +0. Der normale Pre-Push überprüfte die statischen Spiel-Ledger und die vom Repository geforderten WorldBuilder-Nachweise; es gab keine geänderte produktive Spielquelle, die einen zusätzlichen Game-Byte-Selektor benötigt hätte.

Die vollständige Bestandsaufnahme im Bündel steht unter `targets/game/reverse/attempt_support/20261026-mcmickey93-pause.md`. Sie enthält die einzelnen Commit-SHAs, nativen Run-Verweise und offenen Identitäts-, Layout- und Compilerblocker. Die bevorzugten nicht exakten Banken bleiben als Belege gekennzeichnet. Alle Arbeitsreservierungen sind freigegeben; keine Quelländerung blieb uncommittet.

## BFME 2

[PR114](https://github.com/Open-BFME/Open-BFME-2/pull/114) ist geschlossen. Sein unveränderter Dekal-Quellblob wurde unter [e3599c8](https://github.com/Open-BFME/Open-BFME-2/commit/e3599c80e1b9de61b5e7e8254804312e753842e1) in den Hauptzweig integriert. Die sechs bestehenden nativen Körper mit 326 Bytes sind erhalten; neue C++-Exact-Bytes: 0.

Der zuletzt bereits laufende [Auswahllauf 40295476220](https://github.com/McMickey93/Open-BFME-2/actions/runs/40295476220) ist erfolgreich beendet. Es wurden daraus keine neue Funktion und kein Trust237-Versuch begonnen. Sein Fortschrittsbericht nennt BYTE-MATCHED 100% und C++ exact 7.984.346 Bytes, Delta +0. Frühere übernommene Beiträge werden nicht nochmals als Fortschritt gezählt.

## Spätere Wiederaufnahme

Erst nach einem neuen Arbeitsauftrag fortsetzen. Nach dem Herunterladen des Bündels lässt sich die unveränderte Commit-Kette in einem BFME-1-Checkout so prüfen und importieren:

```sh
git fetch https://github.com/Open-BFME/Open-BFME-1.git 7c1af3127d2e0b85ad028605e61b916b98e9dbba
git bundle verify banked-attempts.bundle
git fetch ./banked-attempts.bundle refs/heads/codex/20261026-native-contributions
git log --stat FETCH_HEAD
```

Vor einer späteren Integration erneut die dann aktuellen AGENTS.md und Projektwerkzeuge benutzen und die normalen Prüfungen ausführen. Keine automatische Fortsetzung ist eingerichtet.
