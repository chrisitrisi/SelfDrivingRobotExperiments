# SelfDrivingRobotExperiments

Wir verwenden ein vorgegebenes Modellfahrzeug als Basis. Wir entwickeln dafür eine eigene Platine, programmieren die Fahrzeugsoftware neu und erstellen ein eigenes 3D-Modell. Zusätzliche Entfernungssensoren sind eine Option.

| Bereich | Arbeitsstand |
| --- | --- |
| Hardware (Christopher) | [PCB](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/PCB/PCB) enthält KiCad-Projekte, darunter den Liniensensor. |
| Software | [Main_code](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/Main_code), [code](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/code) und [Test](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/Test) enthalten ESP-IDF-Sensorversuche. Den Ausgangsbranch pro Aufgabe im Issue angeben. |
| 3D-Design | [3D_Design](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/3D_Design/3D_Design-Modelling) enthält Fahrzeug- und Gehäusemodelle sowie Exporte. |
| Diplomarbeitsunterlagen | [Dokumentation](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/Dokumentation/Dokumentation) |

## Gemeinsam arbeiten

1. Erstellt ein [Issue](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/issues/new) mit Ziel, Rolle, Ausgangsbranch und einem überprüfbaren Ergebnis. Bei Aufgaben für mehrere Bereiche beschreibt ihr die Teilaufgaben im selben Issue.
2. Lest die aktuelle [AGENTS.md](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/blob/master/AGENTS.md), die [Schnittstellen](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/blob/master/docs/schnittstellen.md) und die neuesten Issue-Kommentare. Die zentralen Dateien liegen auf `master`, auch wenn ihr gerade einen anderen Branch bearbeitet.
3. Erstellt euren Aufgabenbranch vom vereinbarten Fachbranch. Öffnet den Pull Request zurück in diesen Fachbranch und verlinkt das Issue. Änderungen an gemeinsamen Regeln und Schnittstellen gehen in einen eigenen Pull Request gegen `master`.
4. Haltet im Issue fest, was geprüft wurde, was offen ist und von welcher Rolle ihr eine Antwort braucht.

### Projektstart im Terminal

Mit Python 3 und einer über `gh auth login` angemeldeten GitHub CLI könnt ihr im aktualisierten `master`-Checkout den Kontext zu einer Aufgabe anzeigen. Ersetzt 12 durch eine echte Issue-Nummer:

```sh
python tools/projektstart.py 12
```

Das Skript liest Regeln und Schnittstellen von GitHub sowie das Issue mit seinen Kommentaren. Es wechselt keinen Branch. In einem separaten Fachbranch-Checkout könnt ihr das Skript über seinen Pfad im `master`-Checkout starten.

### Prompt für Antigravity, Claude und ChatGPT

> Wir arbeiten in chrisitrisi/SelfDrivingRobotExperiments. Meine Rolle ist [Hardware, Software oder 3D-Design]. Bearbeite Issue #[Nummer]. Lies AGENTS.md und docs/schnittstellen.md vom aktuellen master sowie das Issue mit seinen Kommentaren. Prüfe den dort genannten Fachbranch, bevor du Dateien bearbeitest. Arbeite auf einem Aufgabenbranch und adressiere den Pull Request an den Fachbranch. Teile Ergebnis, Prüfung und offene Fragen im Issue. Falls dir der Zugriff fehlt, benenne die fehlende Datei oder Aktion und liefere einen kopierbaren Entwurf.

Hinterlegt diesen Verweis in Browser-Projekten als Projektanweisung. Öffnet bei lokalen Tools den richtigen Repository-Ordner. Auf älteren Fachbranches können die zentralen Regeldateien fehlen. Gebt den Verweis dann beim Sitzungsstart mit. In Claude-Projekten mit synchronisierten Dateien vor der Arbeit den Stand von `master` aktualisieren und das Issue über ein GitHub-Werkzeug oder als Text bereitstellen.

**Zugriff testen:** Eine Person schreibt ein Prüfwort in ein Test-Issue. Die zweite KI liest es, antwortet im selben Issue und gibt den Kommentarlink zurück. Die dritte KI liest diese Antwort. Damit testet ihr Datei-, Issue- und Kommentarzugriff getrennt.
