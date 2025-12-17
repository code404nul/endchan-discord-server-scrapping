# Endchan Discord Link Scraper (via Tor)

## Description

Outil de scraping qui parcourt **Endchan** via le réseau **Tor** afin d’extraire les **liens d’invitation Discord** publiquement postés sur les boards.

Projet destiné à des usages **OSINT, recherche et analyse de communautés**.

## Fonctionnalités

* Accès à Endchan via Tor (SOCKS5)
* Scraping des threads et posts publics
* Extraction des liens `discord.gg` / `discord.com/invite`
* Déduplication des résultats
* Export (TXT/JSON)

## Prérequis

* Tor actif (ex : `127.0.0.1:9050`)
* Environnement compatible avec l’implémentation du projet

## Utilisation

1. Lancer Tor
2. Démarrer le scraper
3. Les liens détectés sont sauvegardés automatiquement

## Notes

* Respecter des délais entre requêtes
* Les liens peuvent être expirés ou invalides
* Usage responsable uniquement

## Avertissement

Utiliser ce projet de manière responsable. Soyez gentil, pas méchant. (Pas de doxxing, hein...)