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
