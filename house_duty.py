import random
import json
from collections import defaultdict
from datetime import datetime

# --- Konfiguration ---
HAUS_DUTYS = [
    "Küche putzen",
    "Bad putzen",
    "Wohnzimmer aufräumen",
    "Wischen und Staubsaugen",
    "Notion Todo",
]
# Dateiname für das Speichern des Verlaufs
VERLAUF_DATEI = 'haus_duty_verlauf.json'
# Gewichtungsparameter: Basisgewicht für jede Aufgabe
BASIS_GEWICHT = 10
# Reduktionsfaktor: Um wie viel das Gewicht reduziert wird, wenn die Aufgabe kürzlich erledigt wurde
REDUKTIONS_FAKTOR_PRO_TAG = 2 # Reduziert das Gewicht um 2 pro Tag seit der letzten Erledigung
# Minimales Gewicht, um zu vermeiden, dass eine Aufgabe unmöglich wird
MIN_GEWICHT = 1


# --- Hilfsfunktionen ---

def lade_verlauf():
    """Lädt den Verlauf der erledigten Aufgaben aus der JSON-Datei."""
    try:
        with open(VERLAUF_DATEI, 'r') as f:
            # Stellt sicher, dass alle Haus_DUTYS im Verlauf existieren
            verlauf = defaultdict(lambda: None, json.load(f))
    except FileNotFoundError:
        verlauf = defaultdict(lambda: None)
    except json.JSONDecodeError:
        print("Warnung: Verlauf-Datei ist beschädigt. Starte mit leerem Verlauf.")
        verlauf = defaultdict(lambda: None)
        
    # Füllt fehlende Dutys mit None, falls sie neu sind
    for duty in HAUS_DUTYS:
        if duty not in verlauf:
            verlauf[duty] = None
            
    return verlauf

def speichere_verlauf(verlauf):
    """Speichert den aktuellen Verlauf in der JSON-Datei."""
    with open(VERLAUF_DATEI, 'w') as f:
        # Konvertiere defaultdict zurück in dict für das Speichern
        json.dump(dict(verlauf), f, indent=4)

def berechne_gewichte(duties, verlauf):
    """Berechnet die aktuellen Wahrscheinlichkeitsgewichte."""
    heute = datetime.now().date()
    gewichte = []
    
    for duty in duties:
        gewicht = BASIS_GEWICHT
        letzte_erledigung = verlauf.get(duty)
        
        if letzte_erledigung:
            try:
                # Datum der letzten Erledigung konvertieren
                datum_erledigt = datetime.strptime(letzte_erledigung, '%Y-%m-%d').date()
                # Tage seit der letzten Erledigung berechnen
                tage_seit_erledigung = (heute - datum_erledigt).days
                
                # Gewichtung reduzieren, wenn die Aufgabe kürzlich erledigt wurde
                reduktion = max(0, BASIS_GEWICHT - (tage_seit_erledigung * REDUKTIONS_FAKTOR_PRO_TAG))
                gewicht = max(MIN_GEWICHT, gewicht - reduktion)
                
            except ValueError:
                # Falls das gespeicherte Datum ungültig ist, Basisgewicht verwenden
                pass 
        
        gewichte.append(gewicht)
        print(f"[{duty}]: Gewicht = {gewicht}")

    return gewichte

def waehle_duty(duties, gewichte):
    """Wählt eine Aufgabe zufällig basierend auf den Gewichten aus."""
    # random.choices() wählt ein Element aus der population (duties) basierend auf den weights
    # k=1 wählt nur ein Element
    ausgewaehlte_duty = random.choices(duties, weights=gewichte, k=1)[0]
    return ausgewaehlte_duty

def fuehre_programm_aus():
    """Hauptfunktion des Programms."""
    print("--- Haus Duty Planer ---")
    
    # 1. Verlauf laden
    verlauf = lade_verlauf()
    
    # 2. Gewichte berechnen und anzeigen
    print("\nBerechnete Gewichte (höher = wahrscheinlicher):")
    gewichte = berechne_gewichte(HAUS_DUTYS, verlauf)
    
    # 3. Zufällige Aufgabe wählen
    duty_vorschlag = waehle_duty(HAUS_DUTYS, gewichte)
    
    print("\n-------------------------")
    print(f"Deine heutige Aufgabe: **{duty_vorschlag}**")
    print("-------------------------")
    
    # 4. Verlauf aktualisieren und speichern
    bestaetigung = input(f"\nDuty '{duty_vorschlag}' erledigt? (j/n): ").lower()
    
    if bestaetigung == 'j':
        heute_str = datetime.now().strftime('%Y-%m-%d')
        verlauf[duty_vorschlag] = heute_str
        speichere_verlauf(verlauf)
        print("Aufgabe als erledigt gespeichert. Bis morgen!")
    else:
        print("Aufgabe nicht als erledigt markiert. Das Gewicht ändert sich nicht.")

# --- Programmstart ---
if __name__ == "__main__":
    fuehre_programm_aus()