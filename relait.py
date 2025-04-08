import socket
import threading

class Relai:
    def __init__(self, message):
        self.message = message
        self.interface = "0.0.0.0"
        self.portail = 4400
        self.clients = []
        self.serveurs = []
        self.relai = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.relai.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def ping_reponse(self):
        return len(self.serveurs) >= 1

    def connexion(self):
        try:
            self.relai.bind((self.interface, self.portail))
            self.relai.listen(100)
            print(f"[Relai] En écoute sur {self.interface}:{self.portail}")
            
            while True:
                conn, addr = self.relai.accept()
                signale = conn.recv(4096).decode()

                if signale == "PING":
                    if self.ping_reponse():
                        conn.sendall(b"Disponible")
                    else:
                        conn.sendall(b"Indisponible")
                    conn.close()
                    continue

                if signale == self.message:
                    self.serveurs.append(conn)
                    print(f"[Serveur] {addr[0]} connecté")
                    threading.Thread(target=self.transfer, args=(conn, True), daemon=True).start()

                elif signale == "CLIENT":
                    self.clients.append(conn)
                    print(f"[Client] {addr[0]} connecté")
                    threading.Thread(target=self.transfer, args=(conn, False), daemon=True).start()

                elif signale == "CLIENT_RECEPTION":
                    self.clients.append(conn)
                    print(f"[Client Réception] {addr[0]} connecté")
                    threading.Thread(target=self.transfer, args=(conn, False), daemon=True).start()

        except Exception as e:
            print(f"[Erreur] Connexion : {e}")
        finally:
            self.relai.close()

    def transfer(self, conn, is_serveur):
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                    
                if is_serveur:
                    for client in self.clients[:]:  
                        try:
                            client.sendall(data)
                        except:
                            self.clients.remove(client)
                else:
                    for serveur in self.serveurs[:]:
                        try:
                            serveur.sendall(data)
                        except:
                            self.serveurs.remove(serveur)
        except Exception as e:
            print(f"[Erreur] Transfert : {e}")
        finally:
            try:
                conn.close()
                if conn in self.clients:
                    self.clients.remove(conn)
                if conn in self.serveurs:
                    self.serveurs.remove(conn)
            except:
                pass

if __name__ == "__main__":
    relais = Relai("SERVEUR")
    relais.connexion()