import os
import requests
from vinted_scraper import VintedScraper

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Ricerca ampia e tecnica
BRANDS = "omega zenith longines universal geneve heuer lemania valjoux eta tudor breitling yema squale enicar movado landeron sellita rado"
GIAPPONESI = "seiko pogue kakume ufo 6139 6138 panda bullhead citizen 8110 8100 walter wolf flyback"
VALORE = "nos fondo di magazzino scatola garanzia box papers full set mai indossato intonso coevo bachelite"
KEYWORDS = "cronografo automatico vintage diver chronograph"

RICERCA = f"{BRANDS} {GIAPPONESI} {VALORE} {KEYWORDS}"
BUDGET_MASSIMO = 1500 

scraper = VintedScraper("https://www.vinted.it")

def invia_notifica(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Rimosso Markdown per evitare l'errore 400 se i titoli hanno caratteri strani
    payload = {"chat_id": CHAT_ID, "text": messaggio}
    try:
        r = requests.post(url, json=payload)
        print(f"Risultato invio Telegram: {r.status_code}")
        if r.status_code != 200:
            print(f"Dettaglio errore: {r.text}")
    except Exception as e:
        print(f"Errore connessione: {e}")

def analizza_affare(titolo, prezzo):
    t = titolo.lower()
    if any(box in t for box in ["scatola", "full set", "corredo"]): return "📦 [FULL SET]"
    if any(jap in t for jap in ["6139", "6138", "8110"]): return "🇯🇵 [CHRONO JAP]"
    if any(cond in t for cond in ["nos", "fondo di magazzino"]): return "🌟 [NOS]"
    return "🔍 [RILEVATO]"

def controlla_vinted():
    print(f"Avvio scansione per: {RICERCA}")
    params = {"search_text": RICERCA, "order": "newest_first", "price_to": BUDGET_MASSIMO, "catalog_ids": "79"}
    
    try:
        items = scraper.search(params)
        if not items:
            invia_notifica("⚪ Check completato: Nessun nuovo annuncio.")
            return

        for item in items[:3]:
            prezzo = float(item.price)
            titolo = item.title
            tag = analizza_affare(titolo, prezzo)
            link = f"https://www.vinted.it{item.url}"
            
            testo = f"{tag}\nModello: {titolo}\nPrezzo: {prezzo}€\nLink: {link}"
            invia_notifica(testo)
                
    except Exception as e:
        invia_notifica(f"⚠️ Errore tecnico: {e}")

if __name__ == "__main__":
    controlla_vinted()
