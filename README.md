# BankInzicht

BankInzicht is een Python-applicatie waarmee je eenvoudig overzichten en grafieken maakt van CSV-uitreksels van je bankafschriften. De applicatie draait in een desktop omgeving met een moderne web-interface.

## Features

### Ondersteunde banken
- **ING** - Automatische detectie van ING CSV-formaat
- **Rabobank** - Automatische detectie van Rabobank CSV-formaat

### Overzichten en Analyses
- 📊 **Maandelijkse overzichten** - Inkomsten, uitgaven en netto per maand
- 🏢 **Tegenpartij analyse** - Overzicht per tegenpartij met netto bedragen
- 🏷️ **Label categorisering** - Groepeer transacties op eigen labels
- 💼 **Zakelijk/Privé scheiding** - Filter en analyseer zakelijke vs. privé uitgaven
- 📈 **Grafieken** - Visuele weergave van financiële data

### Functionaliteiten
- **Automatische IBAN filtering** - Interne overboekingen worden automatisch gefilterd
- **Configureerbare negeerlijst** - Sluit bepaalde tegenpartijen uit via `settings.toml` (bijvoorbeeld je eigen spaarrekening)
- **Persistent labeling** - Labels worden opgeslagen in de database los van CSV-bestanden - zodat je labels kunt hergebruiken
- **Desktop applicatie** - Geen browser vereist, draait als standalone app

## Installatie

### Automatische installatie (Windows)
1. Zorg ervoor dat je **Python 3.8+** hebt geïnstalleerd
2. Download of clone dit project
3. Dubbelklik op `setup.bat`
4. De applicatie start automatisch!

### CSV-bestanden toevoegen
- Plaats je bankafschrift CSV-bestanden in de `/data` map
- De applicatie detecteert automatisch het bank-formaat (indien ondersteund)
- Meerdere bestanden kunnen tegelijk worden verwerkt
