# Projet Portfolio #1 — Scanner de ports Python

**Catégorie :** Fondamentaux (Phase 0) — Reconnaissance réseau
**Stack :** Python 3, module `socket`, `sys`, `threading`

---

## Objectif

Recoder un mini-scanner de ports en Python, sans copier de tutoriel, en comprenant chaque ligne du code — de la connexion TCP brute jusqu'à la parallélisation. Le but n'était pas de reproduire Nmap, mais de comprendre **ce qu'un outil comme Nmap fait réellement en dessous** : établir une connexion TCP, interpréter la réponse, et en déduire l'état d'un port.

## Méthodologie

Le projet a été construit de façon incrémentale, chaque brique étant testée individuellement avant d'être intégrée :

1. **Connexion TCP brute** avec le module `socket` (`AF_INET`, `SOCK_STREAM`) et `connect_ex()` pour tester un port sans lever d'exception bloquante — retour `0` si le port est ouvert.
2. **Structuration en fonction** avec `return` plutôt que `print()`, pour que le résultat (`True`/`False`) soit réutilisable dans une logique de décision (`if`) ailleurs dans le script — distinction validée empiriquement en observant le comportement de `None` par défaut sans `return`.
3. **Gestion d'erreurs** avec `try`/`except`, en capturant spécifiquement `socket.gaierror` (résolution DNS invalide) plutôt qu'un `except:` générique, pour que le script continue de tester les autres ports au lieu de planter au premier problème rencontré.
4. **Interface en ligne de commande** avec `sys.argv`, incluant une garde de sécurité (`len(sys.argv) < 2`) pour éviter un `IndexError` si aucune cible n'est fournie.
5. **Validation croisée** : les résultats du scanner ont été comparés à un scan Nmap réel (`nmap -sV`) sur la même cible légale (`scanme.nmap.org`), confirmant la cohérence entre les deux outils (ports 22 et 80 détectés comme ouverts dans les deux cas).
6. **Parallélisation** avec le module `threading` (`.start()` / `.join()`), pour réduire le temps total de scan en testant plusieurs ports simultanément plutôt que séquentiellement.

## Code final (version threadée)

```python
import socket
import sys
import threading

def scanner_port(cible, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        resultat = s.connect_ex((cible, port))
        s.close()
        if resultat == 0:
            print(f"Port {port} : OUVERT")
    except socket.gaierror:
        print(f"Erreur : impossible de résoudre {cible}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

if len(sys.argv) < 2:
    print("Utilisation : python3 scanner.py <cible>")
    sys.exit(1)

cible = sys.argv[1]
ports_a_tester = [21, 22, 25, 80, 443]

threads = []
for port in ports_a_tester:
    t = threading.Thread(target=scanner_port, args=(cible, port))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Scan terminé")
```

## Ce que j'ai appris / ce que je ferais différemment

- **La distinction `print()` vs `return`** n'est pas un détail syntaxique : une fonction utilisant `print()` au lieu de `return` renvoie `None` par défaut, ce qui casse silencieusement toute logique conditionnelle basée sur son résultat — piège rencontré concrètement en testant le comportement plutôt qu'en le lisant simplement.
- **Capturer des erreurs précises** (`socket.gaierror`) plutôt qu'un `except:` générique donne une information exploitable sur la cause d'un échec, utile en reconnaissance réelle où chaque type d'erreur est une donnée sur la cible.
- **Le threading naïf a une limite** : lancer un grand nombre de threads sans contrôle peut saturer la machine locale ou générer un pattern de connexions simultanées facilement détectable côté cible. Une version plus aboutie utiliserait un `ThreadPoolExecutor` avec un nombre de threads limité, plutôt que de tous les lancer d'un coup.
- **Prochaine itération envisagée** : ajouter la détection de bannière (lire les premiers octets renvoyés par un port ouvert) pour se rapprocher du comportement `-sV` de Nmap, et comparer les résultats obtenus via `requests` (en-tête `Server`) pour les ports HTTP.

---

*Testé exclusivement sur `scanme.nmap.org`, cible mise à disposition publiquement pour l'entraînement, et sur mon propre réseau domestique.*
