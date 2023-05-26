#!/usr/bin/env python3


import os
import socket
from connections import Connections
from listen_server import ListenServer
from command import Command


class Interaction:
    def __init__(self, connections: Connections, server: ListenServer) -> None:
        self._connections = connections 
        self._server = server 
        self._target: (socket.socket | None) = None 
        self._ip: (str | None) = None
        self._pwd = os.getcwd()
    
    @property
    def connections(self) -> Connections:
        return self._connections
    
    @property
    def pwd(self) -> str:
        return self._pwd
    
    @pwd.setter
    def pwd(self, arg) -> None:
        self._pwd = arg
    
    @property
    def target(self) -> (socket.socket | None):
        return self._target

    @target.setter
    def target(self, socket: (socket.socket | None)) -> None:
        self._target = socket
    
    @property
    def ip(self) -> (str | None):
        return self._ip
    
    @ip.setter
    def ip(self, ip: (str | None)) -> None:
        self._ip = ip
    
    def _get_host(self) -> str:
        if self.ip is None:
            return f"\x1b[31mLocalHost\x1b[0m"
        return f"\x1b[34m{self.ip}\x1b[0m"
    
    def _prompt_strint(self):
        prompt = f"\x1b[32m┌╶╶╶(\x1b[34mConnected \x1b[32m: {self._get_host()}\x1b[32m)--[\x1b[34m{self.pwd}\x1b[32m]\n└╶╶$\x1b[0m "
        return prompt
        
    def _remove_target(self) -> None:
        print(f"\x1b[31mConnection reset by peer {self.ip}\x1b[0m")
        self._connections.remove_connection(self.ip)
        self.target = None 
        self.ip = None 
        
    def _handle_command(self, command):
        command = Command(command, self)
        cli = command.get_cli()
        
        match cli:
            
            case None:
                return
            
            case "quit":
                command.quit(self._server)
            
            case "lt" | "connected":
                try:
                    command.connected_targets()
                except Exception as ex:
                    print(f"EXCEPTION 'command.connected_targets()' in {__name__} module --> {ex}")
            
            case "ct" | "connect":
                try:
                    command.connect()
                except Exception as ex:
                    print(f"EXCEPTION 'command.connect()' in {__name__} module --> {ex}")
            
            case "dt" | "disconnect":
                try:
                    command.disconnect()
                except Exception as ex:
                    print(f"EXCEPTION 'command.disconnect()' in {__name__} module --> {ex}")
            
            case "open":
                try:
                    command.open(cli)
                except Exception as ex:
                    print(f"EXCEPTION 'command.open(cli)' in {__name__} module --> {ex}")
            
            case "clear":
                try:
                    command.clear(cli)
                except Exception as ex:
                    print(f"EXCEPTION 'command.clear(cli)' in {__name__} module --> {ex}")
            
            case "-h" | "--help":
                try:
                    with open("helpt.txt", "r") as f:
                        help = f.read()
                    print(help)
                except Exception as ex:
                    print(f"EXCEPTION '--help' in {__name__} module --> {ex}")
            
            case "nano" | "vim" | "nvim" | "python" | "Python" | "node":
                print("Not supported operation.")
            
            case "uf" | "upload":
                try:
                    command.upload()
                except Exception as ex:
                    print(f"EXCEPTION 'command.upload()' in {__name__} module --> {ex}")
            
            case "df" | "download":
                try:
                    command.download()
                except Exception as ex:
                    print(f"EXCEPTION 'command.download()' in {__name__} module --> {ex}")
            
            case "udir" | "uploaddir":
                try:
                    command.upload_directory()
                except Exception as ex:
                    print(f"EXCEPTION 'command.upload_directory()' in {__name__} module --> {ex}")
                    
            case "ddir" | "downloaddir":
                try:
                    command.download_directory()
                except Exception as ex:
                    print(f"EXCEPTION 'command.download_directory()' in {__name__} module --> {ex}")
                    
            case _:
                try:
                    command.execute(cli, self.target)
                except socket.error as e:
                    print("Socket error occurred:", e)
                    self._remove_target()
                except Exception as ex:
                       print(f"EXCEPTION 'command.execute(cli, self.target)' in {__name__} module --> {ex}")
                  
    def get_command(self):
        try:
            while True:
                command = input(self._prompt_strint())
                self._handle_command(command)
        except ConnectionAbortedError:
            print(f"The program has been closed !")
        except Exception as ex:
            print(f"[EXCEPTION in Interaction]: {ex}")            