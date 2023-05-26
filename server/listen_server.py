#!/usr/bin/env python3


import socket 
from connections import Connections


Host = str 
Port = int


class ListenServer:
    def __init__(self, connections: Connections, host: Host = "192.168.1.38", port: Port = 8080) -> None:
        self._host = host 
        self._port = port 
        self._connections = connections

    def _handle_connection(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        self._connections.add_connection(conn, addr)
        print(f"\x1b[32mNew client connected --> \x1b[34m{addr[0]}\x1b[32m:\x1b[34m{addr[1]}.\n\x1b[0mPress 'Enter' .. .. .. ")
        
    def create_server(self) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((self._host, self._port))
    
    @property 
    def server(self) -> socket.socket:
        return self._server
    
    def listen(self) -> None:
        self.create_server()
        self._server.listen()
        print(f"The server is listening on {self._host}:{self._port}.\nPress 'Enter' .. .. .. ")
        try:
            while True:
                conn, addr = self._server.accept()
                self._handle_connection(conn, addr)
        except ConnectionAbortedError as ex:
            print(f"The server has been disconnected !")
        except Exception as ex:
            print(f"EXCEPTION in listen_server --> {ex}")       