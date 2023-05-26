#!/usr/bin/env python3


import socket 


class Connection:
    def __init__(self, host: str="192.168.1.38", port: int=8080) -> None:
        self._host = host 
        self._port = port 
    
    def _create_client_socket(self) -> None:
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self) -> socket.socket:
        self._create_client_socket()
        print(f"{self._host}:{self._port} Connectiong attempt ... ")
        self._client.connect((self._host, self._port))
        print("<CONNECTED>")
        return self._client 