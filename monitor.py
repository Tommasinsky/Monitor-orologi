import os
import requests
from vinted_scraper import VintedScraper

# Caricamento credenziali dalle Secrets di GitHub
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
        response = requests.post(url, json=payload)
        # Stampa a video il risultato per il log di GitHub
        print(f"Risultato invio Telegram: {response.status_code}")
    except Exception as e:
        print(f"Errore critico invio: {e}")

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
    # --- MESSAGGIO DI CONTROLLO INIZIALE ---
    invia_notifica("🚀 **Il monitor è partito!** Sto controllando Vinted...")
    
    print(f"Avvio scansione per: {RICERCA}")
    
    params = {
        "search_text": RICERCA,
        "order": "newest_first",
        "price_to": BUDGET_MASSIMO,
        "catalog_ids": "79" 
    }
    
    try:
        items = scraper.search(params)
        
        if not items:
            invia_notifica("⚪ **Check completato**: Nessun nuovo annuncio trovato.")
            return

        annunci_validi = items[:5]
        
        if len(annunci_validi) == 0:
            invia_notifica("⚪ **Check completato**: Esito negativo (filtri non superati).")
        else:
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
        invia_notifica(f"⚠️ **Check fallito**: Errore tecnico.\n`{e}`")

if __name__ == "__main__":
    controlla_vinted()
