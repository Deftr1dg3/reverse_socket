#!/usr/bin/env python3


import os
import socket
from listen_server import ListenServer
from execute import Execute
from connections import Connections
from listen_server import ListenServer
from exceptions import NotConnectedToTheTarget, NotEnoughArgumentsProvided, IncompatibleExtension


class Command:
    _execute = Execute()
    
    def __init__(self, command: str, interaction) -> None:
        self._command = command
        self._split_command = command.split()
        self._execute = Execute()
        self._interaction = interaction
        self._connections: Connections = interaction.connections
      
    def get_cli(self) -> (str | None):
        if not self._split_command:
            return None 
        return self._split_command[0]

    def _get_args(self) -> list[str]:
        if len(self._split_command) < 2:
            raise NotEnoughArgumentsProvided("No arguments provided.")
        return self._split_command[1:]
    
    def _validate_path(self, path: str) -> bool:
        if os.path.exists(path):
            return True
        raise FileNotFoundError(f"File with provided path does not exist. -> {path}")

    def _validate_target(self) -> socket.socket:
        target = self._interaction.target 
        if target is not None:
            return target
        raise NotConnectedToTheTarget("Not connected to the target pc.")

    def _get_path_and_destination(self, args: list) -> list:
        n = len(args)
        if n < 2:
            raise NotEnoughArgumentsProvided(f"Expected for two arguments, 'path/to/file' and 'destination/file'. But got --> {args}")
        if n > 2:
            raise TypeError(f"Utility takes up to two arguments.\n\
                'path/to/file' and 'destination/path'.\n\
                    But {n} arguments were given --> {args}.")
        return args
        
    def quit(self, server: ListenServer) -> None:
        print("Closing server .. .. ..")
        server.server.close()
        raise ConnectionAbortedError()
    
    def connected_targets(self) -> None:
        connections_list = self._connections.connections_list()
        print(f"Active connections: {connections_list}")
    
    def _connect_by_index(self, index: int) -> None:
        ip, target = self._connections.get_connection_by_index(index)
        self._interaction.target = target
        self._interaction.ip = ip
        print(f"Connected to {ip}.")

    def _connect_by_ip(self, ip: str) -> None:
        target = self._connections.get_connection_by_ip(ip)
        self._interaction.target = target
        self._interaction.ip = ip 
        print(f"Connected to {ip}.")
        
    def connect(self) -> None:
        args = self._get_args()
        arg = args[0]
        if arg.isdigit():
            self._connect_by_index(int(arg))
        else:   
            self._connect_by_ip(arg) 

    def disconnect(self ) -> None:
        self._interaction.target = None
        self._interaction.ip = None
    
    def open(self, cli: str) -> None:
        self._execute.execute_local(cli, self._command)
    
    def clear(self, cli: str) -> None:
        self._execute.execute_local(cli, self._command)
        
    def execute(self, cli, target: (socket.socket | None)) -> None:
        if target is None:
            self._execute.execute_local(cli, self._command)
        else:
            self._execute.excute_on_target_pc(self._command, target)
        if cli == "cd":
            self._interaction.pwd = os.getcwd()
            
    def _validate_extensions(self, path: str, destination: str) -> bool:
        path_extension = path.rpartition(".")[-1]
        destination_extension = destination.rpartition(".")[-1]
        if path_extension == destination_extension:
            return True 
        raise IncompatibleExtension(f"Expected for the same extantions in path and destinaqtion path, But got --> *.{path_extension} and *.{destination_extension}")
        
    def upload(self) -> None:
        target = self._validate_target()
        args = self._get_args()
        origin_path, destination = self._get_path_and_destination(args)
        self._validate_path(origin_path)
        self._validate_extensions(origin_path, destination)
        self._execute.upload(target, origin_path, destination)
         
    def download(self):
        target = self._validate_target()
        args = self._get_args()
        origin_path, destination = self._get_path_and_destination(args)
        self._validate_path(os.path.dirname(destination))
        self._validate_extensions(origin_path, destination)
        self._execute.download(target, origin_path, destination)
        
    def upload_directory(self) -> None:
        target = self._validate_target()
        args = self._get_args()
        origin_path, destination = self._get_path_and_destination(args)
        self._validate_path(origin_path)
        self._execute.upload_dir(target, origin_path, destination)
        
    def download_directory(self):
        target = self._validate_target()
        args = self._get_args()
        origin_path, destination = self._get_path_and_destination(args)
        self._validate_path(destination)
        self._execute.download_dir(target, origin_path, destination)