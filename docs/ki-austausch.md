# KI-Austausch zwischen den Rollen

Jede Person im Team arbeitet mit ihrer eigenen KI (Claude, ChatGPT/Codex, Antigravity, …). Wenn eine KI eine Frage an eine andere Rolle hat, fragt sie nicht ihren Menschen, sondern **stellt die Frage als GitHub-Issue an die Zielrolle**. Die KI der Zielrolle beantwortet sie im selben Issue. Menschen müssen nur eingreifen, wenn eine Entscheidung nötig ist.

```
Software-KI ──(Issue „KI-Frage“, Label an:hardware)──▶ GitHub ──▶ Hardware-KI
            ◀──────────── Antwort als Kommentar ───────────────┘
```

## Rollen und Labels

| Rolle | Label für Fragen an diese Rolle | Wissensdatei | Antwortet |
|---|---|---|---|
| Hardware (Christopher) | `an:hardware` | [docs/rollen/hardware.md](rollen/hardware.md) | **automatisch** (GitHub Action) + Posteingang |
| Software | `an:software` | [docs/rollen/software.md](rollen/software.md) | **automatisch** (Antworten + Code-PRs nach `code`) + Posteingang |
| 3D-Design | `an:3d` | [docs/rollen/3d-design.md](rollen/3d-design.md) | Posteingang |

Weitere Labels:

| Label | Bedeutung |
|---|---|
| `ki-frage` | Issue ist eine Frage zwischen KIs |
| `von:hardware` / `von:software` / `von:3d` | wer fragt |
| `beantwortet` | die Ziel-KI hat geantwortet, Fragende prüft |
| `braucht-mensch` | Antwort braucht eine Entscheidung oder Freigabe eines Menschen |

## 1. Frage stellen (fragende KI)

Vorher prüfen, ob die Antwort schon in `docs/schnittstellen.md`, in der Wissensdatei der Zielrolle oder in einem offenen `ki-frage`-Issue steht.

**Mit GitHub CLI** (Claude Code, Codex, Antigravity mit Terminal):

```sh
gh issue create -R chrisitrisi/SelfDrivingRobotExperiments \
  --title "[KI-Frage] Welcher GPIO ist MUX_RSTn?" \
  --label ki-frage --label an:hardware --label von:software \
  --body "Kontext: Ich portiere main.cpp (Branch code) auf ESP32-S3 und brauche den Reset-Pin des TCA9548A.
Frage: Welcher GPIO steuert MUX_RSTn, und ist er aktiv LOW?
Gebraucht für: Issue #3"
```

**Im Browser:** [neues Issue mit Vorlage „KI-Frage“](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/issues/new?template=ki-frage.yml). Kann die KI nicht selbst schreiben, gibt sie den Text als Entwurf aus und der Mensch fügt ihn ein.

Eine gute Frage enthält: **eine** konkrete Frage, den Kontext (Datei + Branch), wofür die Antwort gebraucht wird, und falls vorhanden einen Vorschlag („Ich würde X annehmen – stimmt das?“).

## 2. Antworten (Ziel-KI)

**Posteingang prüfen** – zu Beginn jeder Sitzung:

```sh
gh issue list -R chrisitrisi/SelfDrivingRobotExperiments --state open --label ki-frage --label an:software
```

(`an:software` durch die eigene Rolle ersetzen.)

Antwort als Kommentar im Issue, immer in dieser Form:

```markdown
<!-- ki-antwort:software -->
**🤖 KI-Antwort Software** (von der KI erstellt, vom Menschen noch nicht geprüft)

**Antwort:** …

**Quelle:** Link auf Datei mit Branch oder Commit (z. B. …/blob/PCB/PCB/Tumbler_Mainboard/README_Schaltplan.md)

**Status:** freigegeben | Arbeitsstand | Annahme | offen

**Braucht Mensch:** nein | ja – weil …
```

Danach Label `beantwortet` setzen (`gh issue edit <nr> --add-label beantwortet`). Bei „Braucht Mensch: ja“ zusätzlich `braucht-mensch`.

**Regeln für die antwortende KI**

- Nur antworten, was in den Dateien des Repos steht. Jede Zahl mit Quelle (Datei, Branch/Commit, Revision).
- Nichts erfinden. Steht es nirgends: so sagen, `braucht-mensch` setzen.
- Keine Entscheidungen treffen, die Hardware, Gehäuse oder Schnittstellen ändern. Vorschläge sind erlaubt, aber als „Vorschlag“ markieren.
- Keine Dateien ändern, nichts committen – Antworten nur als Kommentar.

## 3. Nachfragen und Abschluss

- Rückfrage im selben Issue. Für die automatische Hardware-KI: `@hw-ki` in den Kommentar schreiben.
- Die **fragende** KI schließt das Issue, wenn die Antwort reicht, und trägt vereinbarte Werte in `docs/schnittstellen.md` ein (per Pull Request gegen `master`).
- Menschen sehen über das Label `braucht-mensch`, wo sie gebraucht werden:
  [offene Entscheidungen](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/issues?q=is%3Aopen+label%3Abraucht-mensch)

## Automatische Hardware-KI (GitHub Action)

`.github/workflows/ki-hardware.yml` startet Claude, sobald ein Issue mit `an:hardware` (oder Vorlage „KI-Frage“ an Hardware) erstellt wird oder ein Kommentar `@hw-ki` enthält. Claude liest dann diese Datei, `docs/rollen/hardware.md` und die KiCad-Unterlagen vom Branch `PCB` und antwortet im Issue – auch wenn Christopher offline ist.

Einrichtung (einmalig, durch Repo-Owner):

1. Im Terminal `claude setup-token` ausführen (Claude-Pro/Max-Abo) **oder** einen API-Key unter console.anthropic.com anlegen.
2. GitHub → Settings → Secrets and variables → Actions → *New repository secret*:
   `CLAUDE_CODE_OAUTH_TOKEN` (aus Schritt 1) bzw. `ANTHROPIC_API_KEY`.
3. Unter Actions einmal den Workflow **KI-Labels anlegen** starten.

## Automatische Software-KI (GitHub Action)

`.github/workflows/ki-software.yml` startet Claude bei Issues mit `an:software` (oder Vorlage „KI-Frage“ an Software) und bei Kommentaren mit `@sw-ki` – im Issue oder im Pull Request.

- **Frage** → Antwort als Kommentar im Issue (Format wie oben).
- **Auftrag** (Code ändern) → Claude arbeitet im Branch `ki/issue-<nr>` (von `code` abgezweigt) und öffnet einen **Pull Request nach `code`**. Danach baut GitHub den Stand mit ESP-IDF v5.1.2 und schreibt das Ergebnis (✅/❌) in den PR.
- **Nachbessern:** im PR kommentieren, z. B. `@sw-ki Kanal 3 liefert keine Werte, bitte prüfen.`
- **Gemergt wird nie automatisch.** Die Software-Rolle flasht den PR-Stand, testet auf der Platine und merged selbst.
- Ausnahme von der Regel „keine Dateien ändern“: Nur die Software-KI darf – ausschließlich in `ki/issue-*`-Branches – Code ändern.

Die Software-Rolle bekommt Bescheid über GitHub → Repo → **Watch → Custom → Issues + Pull requests**.

Die automatische KI kennt **nur, was auf GitHub liegt**. Neue Schaltplanstände müssen also gepusht werden, damit sie korrekt antworten kann. Andere Rollen können eine eigene Kopie des Workflows anlegen (Rolle, Label, Branch und Trigger-Wort ändern) und dafür ihr eigenes Token hinterlegen.
