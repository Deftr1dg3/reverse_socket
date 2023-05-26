#!/usr/bin/env python3


import os 
import socket
import json
import struct
from typing import Any
from tqdm import tqdm, trange
from exceptions import PathDoesNotExist


class File:
    def __init__(self, target: socket.socket, path: str, destination: str) -> None:
        self._target = target
        self._path = path 
        self._destination = destination
        self._chunck_size = 1024
        
    def _create_packet(self, data: str) -> bytes:
        data_bytes = data.encode("utf-8")
        length = len(data_bytes)
        size = struct.pack("<L", length)
        packet = size + data_bytes
        return packet
            
    def _send_packet(self, packet: bytes) -> None:
        self._target.sendall(packet)
        
    def _get_packet(self) -> str:
        response_length = struct.unpack("<L", self._target.recv(4))[0]
        raw_response = self._target.recv(response_length)
        str_response = raw_response.decode("utf-8")
        return str_response
    
    def _create_json_packet(self, file_info: Any) -> bytes:
        file_info_serialized = json.dumps(file_info)
        file_info_bytes = file_info_serialized.encode("utf-8")
        size = struct.pack("<L", len(file_info_bytes))
        packet = size + file_info_bytes
        return packet
    
    def _get_json_packet(self) -> list:
        info_length = struct.unpack("<L", self._target.recv(4))[0]
        file_info_serialized = self._target.recv(info_length).decode("utf-8")
        file_info = json.loads(file_info_serialized)
        return file_info

    def _get_file_name(self, path: str) -> str:
        file_name = os.path.basename(path)
        return file_name
    
    def _validate_path(self, path: str) -> bool:
        if os.path.exists(path):
            return True
        return False
    
    def _get_path_confirmation(self) -> None:
        confirmation = self._get_packet()
        if confirmation == "<DISAPPROVED>":
            error_message = self._get_packet()
            raise PathDoesNotExist(f"{error_message}")
    
    def _outcome(self) -> str:
        outcome = self._get_packet()
        print(outcome)
        return outcome


class UploadFile(File):
    def _get_folder_location(self, path: str) -> str:
        folder_location = os.path.dirname(path)
        return folder_location
    
    def _split_path(self, path: str) -> list:
        if "/" in path:
            return path.split("/")
        if "\\" in path:
            return path.split("\\")
        else:
            return path.split()
         
    def _get_data_size(self, data: bytes) -> int:
        data_size = len(data)
        return data_size 
    
    def _send_chunck(self, chunck) -> None:
        self._target.sendall(chunck) 
    
    def _get_file_data(self, path: str) -> bytes:
        with open(path, "rb") as f:
            data = f.read()
        return data 
    
    def _upload_data(self, data: bytes, data_size: int) -> None:
        with tqdm(total=data_size) as pbar:
            for i in range(0, data_size, self._chunck_size):
                if data_size < self._chunck_size:
                    self._send_chunck(data[-data_size:])
                    pbar.update(data_size)
                else:
                    self._send_chunck(data[i: i + self._chunck_size])
                    data_size -= self._chunck_size
                    pbar.update(self._chunck_size)
        
    def upload_file(self) -> None:
        data = self._get_file_data(self._path)
        data_size = self._get_data_size(data)
        file_name = self._get_file_name(self._destination)
        destination_location = self._get_folder_location(self._destination)
        destination_list = self._split_path(destination_location)
        
        file_info = [data_size, file_name, destination_list]
        json_packet = self._create_json_packet(file_info)
        self._send_packet(json_packet)
        
        self._get_path_confirmation()
        
        print(f"Uploagin {file_name} .. .. ..")
        self._upload_data(data, data_size)
        self._outcome()
        
        
class DownloadFile(File):
    def _get_chunck(self, chunck_size: (int | None) = None) -> bytes:
        if chunck_size is None:
            chunck_size = self._chunck_size
        chunck = self._target.recv(chunck_size)
        return chunck 
    
    def _download_data(self, data_size: int, save_as: str) -> None:
        data = b""
        with tqdm(total=data_size) as pbar:
            while data_size:
                if data_size < self._chunck_size:
                    chunck = self._get_chunck(data_size)
                    pbar.update(data_size)
                    data_size = 0 
                else:
                    chunck = self._get_chunck()
                    data_size -= self._chunck_size 
                    pbar.update(self._chunck_size)
                data += chunck     
        with open(save_as, "wb") as f:
            f.write(data)
        
    def download_file(self) -> None:
        path = self._create_packet(self._path)
        self._send_packet(path)
        
        self._get_path_confirmation()
        
        file_info = self._get_json_packet()
        data_size  = file_info[0]
        file_name = self._get_file_name(self._destination)
        
        save_as = self._destination
        print(f"Downloading {file_name} .. .. ..")
        self._download_data(data_size, save_as)
        self._outcome()
        print(f"The file has been saved on LOCAL PC as '{save_as}'")
        
    
class UploadDownloadDirectory(UploadFile, DownloadFile):
    def _get_folder(self, path: str) -> str:
        folder_location = os.path.dirname(path)
        return folder_location

    def _get_files(self, path: str) -> list:
        directories = os.walk(path)
        files = [directory[0] + os.sep + file for directory in directories for file in directory[2]]
        return files
    
    def _upload_directory_data(self, directory: list[str]) -> None:
        for file in directory:
            data = self._get_file_data(file)
            data_size = self._get_data_size(data)
            data_size_packet = self._create_packet(str(data_size))
            self._send_packet(data_size_packet)
            print(f"Uploading {file} .. .. ..")
            self._upload_data(data, data_size)
    
    def upload_directory(self): 
        destination_list = self._split_path(self._destination)
        json_path_packet = self._create_json_packet(destination_list)
        self._send_packet(json_path_packet)
        self._get_path_confirmation()
        
        directory = self._get_files(self._path)
        json_directory = self._create_json_packet(directory)
        self._send_packet(json_directory)
        
        self._upload_directory_data(directory)
        
        self._outcome()
      
    def _download_directory_data(self, directory: list[str]):
        for file_path in directory:
            file_name = self._get_file_name(file_path)
            inner_folder = self._get_folder(file_path)
            local_folder = self._destination + os.sep + inner_folder.strip("." + os.sep)
            save_as = local_folder + os.sep + file_name
            os.makedirs(local_folder, exist_ok=True)
            data_size = int(self._get_packet())
            print(f"Downloading {file_path} - size: {data_size} .. .. ..")
            self._download_data(data_size, save_as)  

    def download_directory(self):
        origin_path_list = self._split_path(self._path)
        json_path_packet = self._create_json_packet(origin_path_list)
        self._send_packet(json_path_packet)
        self._get_path_confirmation()
        
        directory = self._get_json_packet()
        
        self._download_directory_data(directory)
        self._outcome()
        print(f"The directory saved in '{self._destination}'")