#!/usr/bin/env python3


from __future__ import annotations
import socket
from exceptions import ClientIsNotConnected


class Connections:
    _instance: dict[type, Connections] = {}
    
    def __new__(cls) -> Connections:
        if not cls._instance.get(cls, False):
            c = super().__new__(cls)
            cls._instance[cls] = c 
        return cls._instance[cls]
    
    def __init__(self) -> None:
        self._connections: dict[str, socket.socket] = {}
        
    def is_connected(self, ip: str) -> bool:
        if ip in self._connections:
            return True 
        return False
        
    def add_connection(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        ip = addr[0]
        self._connections[ip] = conn
    
    def get_connection_by_ip(self, ip: str) -> socket.socket:
        connection = self._connections.get(ip, None)
        if connection is None:
            raise ClientIsNotConnected(f"The client with provided ip --> {ip} is not connected.")
        return connection
    
    def get_connection_by_index(self, index: int) -> tuple:
        if 0 <= index < len(self._connections):
            connection = list(self._connections.items())[index]
            return connection
        else:
            raise IndexError(f"The index --> {index} is out of range.")

    def remove_connection(self, ip: (str | None)) -> None:
        if ip is not None:
            try:
                del self._connections[ip]
            except KeyError:
                pass
    
    def connections_list(self) -> tuple:
        conneected_clients = tuple(self._connections.keys())
        return conneected_clients