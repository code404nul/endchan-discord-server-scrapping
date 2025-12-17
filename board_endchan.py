import requests
import json

# URL du JSON
url = "https://4chan.endchan.net/boards.json"

try:
    # Récupération du JSON
    response = requests.get(url)
    response.raise_for_status()  # Vérifie les erreurs HTTP
    
    # Parse du JSON
    boards = response.json()
    
    # Filtrage des boards avec threadCount >= 30
    filtered_boards = [
        board["board"] 
        for board in boards 
        if board.get("threadCount", 0) >= 30
    ]
    
    # Affichage des résultats
    print(f"Boards avec 30+ threads : {len(filtered_boards)}")
    print("\nListe des boards :")
    for board in filtered_boards:
        print(f"  - {board}")
    
    # Optionnel : sauvegarde dans un fichier
    with open("boards_filtered.json", "w") as f:
        json.dump(filtered_boards, f, indent=2)
    
    print("\n✓ Résultats sauvegardés dans 'boards_filtered.json'")

except requests.RequestException as e:
    print(f"Erreur lors de la requête : {e}")
except json.JSONDecodeError as e:
    print(f"Erreur lors du parsing JSON : {e}")
except KeyError as e:
    print(f"Clé manquante dans le JSON : {e}")