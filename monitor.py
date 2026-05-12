import os
import requests
from vinted_scraper import VintedScraper

# Credenziali dalle Secrets di GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configurazione Radar
# Cerchiamo i "big" del vintage e cronografi di qualità
RICERCA = "omega zenith longines universal geneve heuer lemania valjoux eta"
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
    
    # LOGICA 1: I prezzi "da urlo" (Qualsiasi pezzo top sotto i 450€)
    if prezzo <= 450:
        return "🚨 🔥 **AFFARE CLAMOROSO**\nPrezzo bassissimo per questa categoria. Controlla subito l'originalità!"
    
    # LOGICA 2: I Cronografi di valore (Heuer, Lemania, Universal) sotto i 1000€
    rari = ["heuer", "lemania", "universal", "zenith"]
    if any(brand in t for brand in rari) and prezzo < 1000:
        return "⚡ **PEZZO DA INVESTIMENTO**\nMarchio prestigioso sotto i 1000€. Potrebbe sparire in fretta."
    
    # LOGICA 3: Longines e Omega sotto i 700€
    if any(brand in t for brand in ["omega", "longines"]) and prezzo < 700:
        return "💎 **OTTIMO RAPPORTO QUALITÀ/PREZZO**\nUn classico a prezzo competitivo."
    
    return "🔍 **VALUTAZIONE IN CORSO**\nPrezzo coerente con il mercato, verifica lo stato di conservazione."

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
        if not items: return

        # Monitoriamo i primi 3 nuovi annunci
        for item in items[:3]:
            prezzo = float(item.price)
            titolo = item.title
            valutazione = analizza_affare(titolo, prezzo)
            
            link = f"https://www.vinted.it{item.url}"
            
            messaggio = (
                f"{valutazione}\n\n"
                f"⌚ *Modello:* {titolo}\n"
                f"💰 *Prezzo:* {prezzo}€\n\n"
                f"🔗 [CLICCA QUI PER L'ANNUNCIO]({link})"
            )
            
            invia_notifica(messaggio)
            
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    controlla_vinted()
