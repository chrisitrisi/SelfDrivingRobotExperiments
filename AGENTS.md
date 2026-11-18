# Teamregeln für SelfDrivingRobotExperiments

- Arbeitsort ist `chrisitrisi/SelfDrivingRobotExperiments`. Gemeinsame Regeln und vereinbarte Schnittstellen liegen auf `master`. Lies die README und `docs/schnittstellen.md` von diesem Branch. Prüfe bei lokalen Änderungen das Git-Remote und den aktiven Branch.
- Das Team entwickelt eine neue PCB, neue Fahrzeugsoftware und ein 3D-Modell für ein vorgegebenes Fahrzeug. Christopher verantwortet die Hardware. Weitere Rollen sind Softwareentwicklung und 3D-Design.
- Lies das beauftragte Issue mit allen aktuellen Kommentaren. Prüfe vor der Umsetzung vorhandene Pull Requests und den Fachbranch. Bei mehreren Softwareständen den Ausgangsbranch aus dem Issue verwenden oder mit der Softwareentwicklung klären.
- Entwickle auf einem Aufgabenbranch vom passenden Fachbranch. Richte den PR auf diesen Fachbranch. Regeln und vereinbarte Schnittstellen werden auf Aufgabenbranches von `master` gepflegt und per PR gegen `master` vorgeschlagen.
- Betrifft eine Änderung mehrere Rollen, verlinke die Quelldatei mit Branch oder Commit und stelle die konkrete Frage im Issue. Belege bestätigte Werte mit Quelle und Revision. Versuchswerte, offene Fragen und freigegebene Vorgaben müssen unterscheidbar sein.
- Übergib im Issue das Ergebnis, die durchgeführte Prüfung, offene Punkte und die als Nächstes zuständige Rolle. Verlinke den PR. Wenn ein Werkzeug nur lesen kann, liefere den Kommentar als Entwurf.

## KI-Austausch zwischen den Rollen

- Brauchst du eine Information von einer anderen Rolle, frag nicht deinen Menschen, sondern stelle eine **KI-Frage** als Issue mit den Labels `ki-frage`, `an:<rolle>` und `von:<deine rolle>` (Rollen: `hardware`, `software`, `3d`). Ablauf, Befehle und Antwortformat: `docs/ki-austausch.md`. Das Wissen jeder Rolle steht in `docs/rollen/<rolle>.md`.
- Prüfe zu Beginn jeder Sitzung deinen Posteingang: `gh issue list -R chrisitrisi/SelfDrivingRobotExperiments --state open --label ki-frage --label an:<deine rolle>`. Beantworte offene Fragen nach `docs/ki-austausch.md`, bevor du mit der eigentlichen Aufgabe beginnst.
- Antworte nur mit belegtem Stand aus dem Repository, triff keine Entscheidungen für andere Rollen und setze `braucht-mensch`, wenn ein Mensch entscheiden muss. Fragen an die Hardware beantwortet zusätzlich eine GitHub Action automatisch; Rückfragen dort mit `@hw-ki`.
