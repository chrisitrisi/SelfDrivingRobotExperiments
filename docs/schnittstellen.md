# Schnittstellen am Modellfahrzeug

Die Tabelle unterscheidet vorhandene Versuche und offene Entscheidungen für die neue Platine. Sobald die beteiligten Rollen einen Wert vereinbart haben, tragt ihn hier mit Einheit, Platinen- oder Modellrevision und Link zur Quelldatei bzw. Entscheidung ein.

| Schnittstelle | Stand | Nächste Abstimmung |
| --- | --- | --- |
| PCB ↔ 3D-Modell | Die Fahrzeugbasis ist vorgegeben. Platinenumriss, Befestigungspunkte, Einbauhöhe und Steckerfreiraum der neuen PCB sind hier noch offen. | Hardware und 3D-Design vereinbaren Bezugspunkt, Orientierung und Maße in mm. |
| PCB ↔ Firmware | ESP-IDF-Code zur Sensorerprobung ist vorhanden. Die Pinbelegung der neuen PCB ist offen. | Hardware und Software gleichen Netzname, Steckerpin, GPIO, Signalrichtung und Pegel mit derselben Schaltplanrevision ab. |
| Optionale Abstandssensoren | Ein Versuch liest vier VL53L0X über I²C mit einzelnen XSHUT-Leitungen aus. Auswahl und Anzahl für das Fahrzeug sind offen. | Software dokumentiert den Versuch. Hardware und 3D-Design prüfen Anschluss, Platz und Sichtfeld, sobald ein Sensor ausgewählt ist. |

**Quellen im Repository**

- [Sensorversuch in Main_code](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/blob/78c78468693d7f15c1a7e84a13207e0a665c569f/main/main.cpp)
- [Sensorversuch mit Abfrage auf neue Messwerte](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/blob/6a9f93ee37eea623016d59b57d197092d671ae79/main/main.cpp)
- [KiCad-Unterlagen](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/PCB/PCB) und [Mechanikmodelle](https://github.com/chrisitrisi/SelfDrivingRobotExperiments/tree/3D_Design/3D_Design-Modelling)
