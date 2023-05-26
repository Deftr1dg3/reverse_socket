#!/usr/bin/env python3


import os 
import socket
import json
import struct
from exception import PathDoesNotExist, IncompatibleExtension


class File:
    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock 
        self._chunck_size = 1024
        
    def _create_packet(self, data: str) -> bytes:
        data_bytes = data.encode("utf-8")
        length = len(data_bytes)
        size = struct.pack("<L", length)
        packet = size + data_bytes
        return packet
            
    def _send_packet(self, packet: bytes) -> None:
        self._sock.sendall(packet)
        
    def _get_packet(self) -> str:
        packet_length = struct.unpack("<L", self._sock.recv(4))[0]
        packet_bytes = self._sock.recv(packet_length)
        packet = packet_bytes.decode("utf-8")
        return packet
    
    def _create_json_packet(self, file_info: list) -> bytes:
        file_info_serialized = json.dumps(file_info)
        file_info_bytes = file_info_serialized.encode("utf-8")
        size = struct.pack("<L", len(file_info_bytes))
        packet = size + file_info_bytes
        return packet
    
    def _get_json_packet(self) -> list:
        info_length = struct.unpack("<L", self._sock.recv(4))[0]
        file_info_serialized = self._sock.recv(info_length).decode("utf-8")
        file_info = json.loads(file_info_serialized)
        return file_info
    
    def _get_file_name(self, path: str) -> str:
        file_name = os.path.basename(path)
        return file_name
    
    def _validate_path(self, path: str) -> bool:
        if os.path.exists(path):
            return True
        return False
    
    def _confirm_path_existance(self, path: str) -> None:
        if not self._validate_path(path):
            disapproved = self._create_packet("<DISAPPROVED>")
            self._send_packet(disapproved)
            raise PathDoesNotExist(f"Provided path does not exist on destination machine. --> {path}")
        approved = self._create_packet("<APPROVED>")
        self._send_packet(approved)


class UploadFile(File):
    def _split_path(self, path: str) -> list:
        if "/" in path:
            return path.split("/")
        if "\\" in path:
            return path.split("\\")
        else:
            return path.split()
            
    def _get_file_extension(self, file_name: str) -> str:
        extension = file_name.rpartition(".")[-1]
        return extension
    
    def _get_data_size(self, data: bytes) -> int:
        data_size = len(data)
        return data_size 
    
    def _send_chunck(self, chunck) -> None:
        self._sock.sendall(chunck) 
    
    def _get_file_data(self, path: str) -> bytes:
        with open(path, "rb") as f:
            data = f.read()
        return data 
    
    def _upload_data(self, data: bytes, data_size: int) -> None:
        for i in range(0, data_size, self._chunck_size):
                if data_size < self._chunck_size:
                    self._send_chunck(data[-data_size:])
                else:
                    self._send_chunck(data[i: i + self._chunck_size])
                    data_size -= self._chunck_size
    
    def upload_file(self) -> bytes:
        path = self._get_packet()
        self._confirm_path_existance(path)
        file_name = self._get_file_name(path)
        
        data = self._get_file_data(path)
        data_size = self._get_data_size(data)
        
        file_info = [data_size]
        json_packet = self._create_json_packet(file_info)
        self._send_packet(json_packet)
        
        self._upload_data(data, data_size)
            
        return f"File '{file_name}' uploading process completed successfully.".encode("utf-8")
        
        
class DownloadFile(File):
    def _get_path_from_list(self, destination_list: list) -> str:
        destination = os.sep.join(destination_list)
        return destination
    
    def _get_chunck(self, chunck_size: (int | None) = None) -> bytes:
        if chunck_size is None:
            chunck_size = self._chunck_size
        chunck = self._sock.recv(chunck_size)
        return chunck 

    def _save_as(self, destination: str, file_name: str, ) -> str:
        return destination + os.sep + file_name
    
    def _download_data(self, data_size: int, save_as: str) -> None:
        data = b""
        while data_size:
            if data_size < self._chunck_size:
                chunck = self._get_chunck(data_size)
                data_size = 0 
            else:
                chunck = self._get_chunck()
                data_size -= self._chunck_size 
            data += chunck 
        with open(save_as, "wb") as f:
            f.write(data)  
        
    def download_file(self) -> bytes:
        file_info = self._get_json_packet()
        data_size, file_name, destination_list = file_info
        destination = self._get_path_from_list(destination_list)
        
        self._confirm_path_existance(destination)
        
        save_as = self._save_as(destination, file_name)
        
        self._download_data(data_size, save_as)
            
        return f"The file '{file_name}' has been saved on TARGET PC as {save_as}".encode("utf-8")                   
       
          

class UploadDownloadDirectory(UploadFile, DownloadFile):
    def _get_folder(self, path: str) -> str:
        folder_location = os.path.dirname(path)
        return folder_location
    
    def _get_files(self, path: str) -> list:
        directories = os.walk(path)
        files = [directory[0] + os.sep + file for directory in directories for file in directory[2]]
        return files
    
    def _download_directory_data(self, destination: str, directory: list[str]) -> None:
        for file_path in directory:
            file_name = self._get_file_name(file_path)
            inner_folder = self._get_folder(file_path)
            local_folder = destination + os.sep + inner_folder.strip("." + os.sep)
            save_as = local_folder + os.sep + file_name
            os.makedirs(local_folder, exist_ok=True)
            data_size = int(self._get_packet())
            self._download_data(data_size, save_as)
    
    def download_directory(self) -> bytes:
        destination_list = self._get_json_packet()
        destination = self._get_path_from_list(destination_list)
        self._confirm_path_existance(destination)
        
        directory = self._get_json_packet()
        
        self._download_directory_data(destination, directory)
        
        return f"The directory '{destination}' has been saved on TARGET PC in {destination}".encode("utf-8")                   
    
    
    def _upload_directory_data(self, directory: list[str]) -> None:
        for file in directory:
            data = self._get_file_data(file)
            data_size = self._get_data_size(data)
            data_size_packet = self._create_packet(str(data_size))
            self._send_packet(data_size_packet)
            self._upload_data(data, data_size)
    
    def upload_directory(self) -> bytes:
        origin_path_list = self._get_json_packet()
        origin_path =  self._get_path_from_list(origin_path_list)
        self._confirm_path_existance(origin_path)
        
        directory = self._get_files(origin_path)
        directory_json = self._create_json_packet(directory)
        self._send_packet(directory_json)
        
        self._upload_directory_data(directory)
        
        return f"The directory '{origin_path}' has been saved on LOCAL PC.".encode("utf-8")                   