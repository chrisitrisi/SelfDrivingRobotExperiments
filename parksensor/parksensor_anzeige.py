import math
import os
import tkinter as tk
from tkinter import messagebox

# Sensor: Name, Mittelpunkt der Boegen (relativ zur Automitte), Richtung in Grad, Breite des Bogens, Start-Radius
SENSOREN = [
    ("Vorne",  (0, -60), 90,  70, 66),
    ("Rechts", (0, 0),   0,   50, 75),
    ("Hinten", (0, 60),  270, 70, 66),
    ("Links",  (0, 0),   180, 50, 75),
]

SEGMENTE = 5
SEG_DICKE = 18
SEG_ABSTAND = 5
FARBE_AUS = "#333333"
HINTERGRUND = "#111111"


def farbe_fuer(abstand, max_cm):
    anteil = abstand / max_cm
    if anteil < 0.15:
        return "#e53935"   # rot
    if anteil < 0.35:
        return "#fb8c00"   # orange
    if anteil < 0.6:
        return "#fdd835"   # gelb
    return "#43a047"       # gruen


class ParkAnzeige(tk.Frame):
    def __init__(self, master, max_cm, zurueck):
        super().__init__(master, bg=HINTERGRUND)
        self.max_cm = max_cm
        self.cx, self.cy = 350, 330

        tk.Label(self, text="Parksensoren", fg="white", bg=HINTERGRUND,
                 font=("Arial", 18, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.canvas = tk.Canvas(self, width=700, height=660, bg=HINTERGRUND, highlightthickness=0)
        self.canvas.pack()
        self.warnung = tk.Label(self, text="", fg="#ffcc00", bg=HINTERGRUND, font=("Arial", 14, "bold"))
        self.warnung.pack(pady=5)
        tk.Button(self, text="Neue Werte eingeben", command=zurueck).pack(pady=(0, 10))

        self.zeichne_auto()
        self.segmente = [self.erzeuge_boegen(s) for s in SENSOREN]
        self.texte = [self.erzeuge_text(s) for s in SENSOREN]

    def zeichne_auto(self):
        c, x, y = self.canvas, self.cx, self.cy
        bild = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto.png")
        if os.path.exists(bild):
            self.auto_bild = tk.PhotoImage(file=bild)  # merken, sonst loescht Python das Bild
            c.create_image(x, y, image=self.auto_bild)
        else:
            c.create_rectangle(x - 55, y - 105, x + 55, y + 105, fill="#dddddd", outline="#ffffff", width=2)

    def erzeuge_boegen(self, sensor):
        _, (dx, dy), richtung, breite, r0 = sensor
        mx, my = self.cx + dx, self.cy + dy
        boegen = []
        for i in range(SEGMENTE):
            r = r0 + i * (SEG_DICKE + SEG_ABSTAND) + SEG_DICKE / 2
            boegen.append(self.canvas.create_arc(
                mx - r, my - r, mx + r, my + r,
                start=richtung - breite / 2, extent=breite,
                style=tk.ARC, width=SEG_DICKE, outline=FARBE_AUS))
        return boegen

    def erzeuge_text(self, sensor):
        name, (dx, dy), richtung, _, r0 = sensor
        r = r0 + SEGMENTE * (SEG_DICKE + SEG_ABSTAND) + 25
        w = math.radians(richtung)
        x = self.cx + dx + r * math.cos(w)
        y = self.cy + dy - r * math.sin(w)
        return self.canvas.create_text(x, y, text=name, fill="white", font=("Arial", 11, "bold"))

    def setze_abstaende(self, abstaende):
        naechster = min(abstaende)
        for (name, *_), boegen, text, d in zip(SENSOREN, self.segmente, self.texte, abstaende):
            # Je naeher das Hindernis, desto mehr Segmente leuchten (von aussen nach innen)
            if d >= self.max_cm:
                start = SEGMENTE
            else:
                start = int(d / self.max_cm * SEGMENTE)
            farbe = farbe_fuer(d, self.max_cm)
            for i, bogen in enumerate(boegen):
                self.canvas.itemconfig(bogen, outline=farbe if i >= start else FARBE_AUS)
            self.canvas.itemconfig(text, text=f"{name}\n{d:.0f} cm" if d < self.max_cm else f"{name}\nfrei")

        if naechster < self.max_cm * 0.15:
            self.warnung.config(text="⚠ STOPP! Hindernis sehr nah", fg="#e53935")
        elif naechster < self.max_cm:
            self.warnung.config(text="⚠ Fahrweg kontrollieren!", fg="#ffcc00")
        else:
            self.warnung.config(text="Alles frei", fg="#43a047")


class EingabeFenster(tk.Frame):
    def __init__(self, master, start, werte, max_cm):
        super().__init__(master, padx=30, pady=20)
        tk.Label(self, text="Abstaende eingeben (in cm)", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))
        self.felder = []
        for i, (name, *_) in enumerate(SENSOREN):
            tk.Label(self, text=f"{name}:", font=("Arial", 12)).grid(row=i + 1, column=0, sticky="e", pady=4)
            e = tk.Entry(self, width=10, font=("Arial", 12))
            e.insert(0, str(werte[i]))
            e.grid(row=i + 1, column=1, pady=4, padx=5)
            self.felder.append(e)

        tk.Label(self, text="Max. Reichweite:", font=("Arial", 12)).grid(row=6, column=0, sticky="e", pady=(15, 4))
        self.max_feld = tk.Entry(self, width=10, font=("Arial", 12))
        self.max_feld.insert(0, str(max_cm))
        self.max_feld.grid(row=6, column=1, pady=(15, 4), padx=5)

        self.start = start
        tk.Button(self, text="Anzeigen", font=("Arial", 12, "bold"), command=self.ok).grid(
            row=7, column=0, columnspan=2, pady=15)
        master.bind("<Return>", lambda _: self.ok())

    def ok(self):
        try:
            werte = [float(f.get().replace(",", ".")) for f in self.felder]
            max_cm = float(self.max_feld.get().replace(",", "."))
            if max_cm <= 0 or any(w < 0 for w in werte):
                raise ValueError
        except ValueError:
            messagebox.showerror("Fehler", "Bitte nur positive Zahlen eingeben.")
            return
        self.start(werte, max_cm)


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Parksensor-Anzeige")
        self.root.configure(bg=HINTERGRUND)
        self.werte = [80, 25, 50, 8]
        self.max_cm = 100
        self.seite = None
        self.zeige_eingabe()

    def wechsle(self, neue_seite):
        if self.seite:
            self.seite.destroy()
        self.root.unbind("<Return>")
        self.seite = neue_seite
        self.seite.pack(fill="both", expand=True)

    def zeige_eingabe(self):
        self.wechsle(EingabeFenster(self.root, self.zeige_anzeige, self.werte, self.max_cm))

    def zeige_anzeige(self, werte, max_cm):
        self.werte, self.max_cm = werte, max_cm
        self.anzeige = ParkAnzeige(self.root, max_cm, self.zeige_eingabe)
        self.wechsle(self.anzeige)
        self.anzeige.setze_abstaende(werte)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
