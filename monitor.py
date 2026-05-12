import os
import requests
from vinted_scraper import VintedScraper

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# CONFIGURAZIONE RADAR AVANZATA
BRANDS = "omega zenith longines universal geneve heuer lemania valjoux eta tudor breitling yema squale enicar movado landeron sellita rado"
GIAPPONESI = "seiko pogue kakume ufo 6139 6138 panda bullhead citizen 8110 8100 walter wolf flyback"
VALORE = "nos fondo di magazzino scatola garanzia box papers full set mai indossato intonso coevo bachelite"
KEYWORDS = "cronografo automatico vintage diver chronograph"

RICERCA = f"{BRANDS} {GIAPPONESI} {VALORE} {KEYWORDS}"
BUDGET_MASSIMO = 1500 

scraper = VintedScraper("https://www.vinted.it")

def invia_notifica(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Errore invio: {e}")

def analizza_affare(titolo, prezzo):
    t = titolo.lower()
    if any(box in t for box in ["scatola e garanzia", "full set", "corredo"]):
        return "📦 **FULL SET DETECTED**"
    if any(jap in t for jap in ["pogue", "6139", "6138", "bullhead", "8110"]):
        if prezzo < 500:
            return "🇯🇵 **CHRONO JAP AFFARE**"
    if any(cond in t for cond in ["nos", "fondo di magazzino"]):
        return "🌟 **CONDIZIONI PAZZESCHE (NOS)**"
    return "🔍 **RILEVATO**"

def controlla_vinted():
    print("Scansione in corso...")
    params = {
        "search_text": RICERCA,
        "order": "newest_first",
        "price_to": BUDGET_MASSIMO,
        "catalog_ids": "79" 
    }
    
    try:
        items = scraper.search(params)
        
        # CASO 1: Vinted non restituisce proprio nulla
        if not items:
            invia_notifica("⚪ **Check completato**: Nessun nuovo annuncio trovato su Vinted.")
            return

        # Filtriamo gli oggetti (prendiamo solo i più recenti per non intasare)
        annunci_validi = items[:5]
        
        if len(annunci_validi) == 0:
            # CASO 2: Esistono annunci ma nessuno rispetta i parametri (raro con questa ricerca ampia)
            invia_notifica("⚪ **Check completato**: Esito negativo (filtri non superati).")
        else:
            # CASO 3: Trovati annunci!
            for item in annunci_validi:
                prezzo = float(item.price)
                titolo = item.title
                valutazione = analizza_affare(titolo, prezzo)
                link = f"https://www.vinted.it{item.url}"
                
                messaggio = (
                    f"{valutazione}\n\n"
                    f"⌚ *Modello:* {titolo}\n"
                    f"💰 *Prezzo:* {prezzo}€\n\n"
                    f"🔗 [VAI ALL'ANNUNCIO]({link})"
                )
                invia_notifica(messaggio)
                
    except Exception as e:
        # Se c'è un errore tecnico, ti avvisa comunque (così sai perché non ricevi esiti)
        invia_notifica(f"⚠️ **Check fallito**: Errore tecnico durante la scansione.\n`{e}`")

if __name__ == "__main__":
    controlla_vinted()
