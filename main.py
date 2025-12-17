import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

BASE_URL = "http://endchancxfbnrfgauuxlztwlckytq7rgeo5v6pc2zd4nyqo3khfam4ad.onion"

DISCORD_PATTERNS = [
    r'discord\.gg/[a-zA-Z0-9]+',
    r'discord\.com/invite/[a-zA-Z0-9]+',
    r'discordapp\.com/invite/[a-zA-Z0-9]+'
]

def load_boards(filename='boards_filtered.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            boards = json.load(f)
        print(f"✓ {len(boards)} boards chargés depuis {filename}")
        return boards
    except FileNotFoundError:
        print(f"✗ Fichier {filename} non trouvé")
        return []
    except json.JSONDecodeError:
        print(f"✗ Erreur de parsing JSON dans {filename}")
        return []

def extract_discord_links(text):
    links = set()
    for pattern in DISCORD_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # normalisation du liens
            if not match.startswith('http'):
                match = f"https://{match}"
            links.add(match)
    return links

def verifier_lien_discord(lien, session):

    pattern = r'discord(?:\.gg|\.com/invite)/([a-zA-Z0-9-]+)'
    match = re.search(pattern, lien)
    
    if not match:
        return False
    
    code = match.group(1)
    url = f"https://discord.com/api/v10/invites/{code}"
    
    try:
        # Sans tor
        response = session.get(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"    ⚠️  Erreur de vérification: {e}")
        return False

def scrape_page(board, page_num, tor_session, verify_session):
    if page_num == 1:
        url = f"{BASE_URL}/{board}/"
    else:
        url = f"{BASE_URL}/{board}/{page_num}.html"
    
    try:
        print(f"  → Scraping {board} page {page_num}...", end=' ')
        response = tor_session.get(url, proxies=PROXIES, timeout=30)
        
        if response.status_code == 404:
            print("(404 - fin du board)")
            return None, True, 0, 0
        
        if response.status_code != 200:
            print(f"(erreur {response.status_code})")
            return set(), False, 0, 0
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        discord_links = extract_discord_links(page_text)
        
        if not discord_links:
            print("(aucun lien)")
            return set(), False, 0, 0
        
        valid_links = set()
        invalid_count = 0
        
        print(f"({len(discord_links)} trouvés)", end=' ')
        
        for link in discord_links:
            print(".", end='', flush=True)
            if verifier_lien_discord(link, verify_session):
                save_link(board, link)
                valid_links.add(link)
            else:
                save_invalid_link(board, link)
                invalid_count += 1
            
            time.sleep(0.5)
        
        valid_count = len(valid_links)
        print(f" ✓ {valid_count} valides, {invalid_count} invalides")
        
        return valid_links, False, valid_count, invalid_count
        
    except requests.exceptions.Timeout:
        print("(timeout)")
        return set(), False, 0, 0
    except requests.exceptions.RequestException as e:
        print(f"(erreur: {e})")
        return set(), False, 0, 0

def scrape_board(board, max_pages=60, tor_session=None, verify_session=None):
    if tor_session is None:
        tor_session = requests.Session()
    if verify_session is None:
        verify_session = requests.Session()
    
    print(f"\n[{board}] debut du scrapping...")
    all_links = set()
    total_valid = 0
    total_invalid = 0
    
    for page in range(1, max_pages + 1):
        result = scrape_page(board, page, tor_session, verify_session)
        
        if result[0] is None:
            break
        
        links, is_end, valid_count, invalid_count = result
        all_links.update(links)
        total_valid += valid_count
        total_invalid += invalid_count
        
        if is_end: #fin du board
            break
        
        # pause
        time.sleep(2)
    
    print(f"[{board}]liens valides: {total_valid} ; liens invalides: {total_invalid}.")
    return all_links, total_valid, total_invalid

def save_link(board, link, filename='discord_links.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{board}\t{link}\n")

def save_invalid_link(board, link, filename='discord_links_invalid.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{board}\t{link}\n")

def save_final_results(results, filename='discord_links.json'):
    output = {
        'total_links': sum(len(links) for links in results.values()),
        'boards_scraped': len(results),
        'results': {board: list(links) for board, links in results.items()}
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"resultats dans {filename}")

def main():
    output_file = 'discord_links.txt'
    invalid_file = 'discord_links_invalid.txt'
    
    
    boards = load_boards()
    if not boards:
        print("Aucun board à scraper. Vérifiez board_filtered.json")
        return
    
    print("\nVérification de la connexion Tor...")
    try:
        tor_session = requests.Session()
        test = tor_session.get(
            'https://check.torproject.org/api/ip',
            proxies=PROXIES,
            timeout=10
        )
        tor_data = test.json()
        if tor_data.get('IsTor'):
            print(f"via Tor (IP: {tor_data.get('IP')})")
        else:
            print("Pas de tor, quit...")
            return
    except Exception as e:
        print(f"erreur de connexion Tor: {e}")
        print("Tor est-il lancer sur le port 9050 ?")
        return
    
    verify_session = requests.Session()

    all_results = {}
    stats = {'total_valid': 0, 'total_invalid': 0}
    
    for i, board in enumerate(boards, 1):
        print(f"\n[{i}/{len(boards)}] Board: {board}")
        links, valid_count, invalid_count = scrape_board(
            board, 
            max_pages=60, 
            tor_session=tor_session,
            verify_session=verify_session
        )
        all_results[board] = links
        stats['total_valid'] += valid_count
        stats['total_invalid'] += invalid_count
        
        if i < len(boards):
            print(f"Pause...")
            time.sleep(5)
    
    save_final_results(all_results)

if __name__ == "__main__":
    main()