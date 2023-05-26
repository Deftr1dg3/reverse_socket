#!/usr/bin/env python3


import time
from connection import Connection
from interaction import Interaction


TIMEOUT = 5


def connect() -> None:
    connection = Connection()
    sock = connection.connect()
    interaction = Interaction(sock)
    interaction.interact()  


def main() -> None:
    while True:
        try:
            connect()
        except ConnectionRefusedError as ex:
            time.sleep(TIMEOUT)
         
         
def connection_attempt() -> None:
    try:
        main()
    except Exception as ex:
        time.sleep(TIMEOUT)
        connection_attempt()
        

if __name__ == "__main__":
    connection_attempt()