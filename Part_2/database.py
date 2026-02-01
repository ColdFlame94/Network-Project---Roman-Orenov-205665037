from dataclasses import dataclass
from typing import Dict, Optional
import socket

@dataclass
class ClientInfo:
    conn: socket.socket
    addr: tuple
    name: str


class Database:
    """
    In-memory database schema:
    clients:
        name -> ClientInfo
    pairs:
        name -> name of chat partner (None if not in chat)
    """

    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}
        self.pairs: Dict[str, Optional[str]] = {}

    #  Client management
    def add_client(self, client: ClientInfo):
        self.clients[client.name] = client
        self.pairs[client.name] = None

    def remove_client(self, name: str):
        self.clients.pop(name, None)
        self.pairs.pop(name, None)

    def client_exists(self, name: str) -> bool:
        return name in self.clients

    def get_client(self, name: str) -> Optional[ClientInfo]:
        return self.clients.get(name)

    #  Chat management
    def start_chat(self, user1: str, user2: str):
        self.pairs[user1] = user2
        self.pairs[user2] = user1

    def end_chat(self, user: str):
        partner = self.pairs.get(user)
        if partner:
            self.pairs[partner] = None
        self.pairs[user] = None

    def get_partner(self, name: str) -> Optional[str]:
        return self.pairs.get(name)

    def list_clients(self):
        return list(self.clients.keys())
