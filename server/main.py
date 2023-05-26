#!/usr/bin/env python3


import threading
from connections import Connections
from listen_server import ListenServer
from interaction import Interaction


def main():
    connections = Connections()
    server = ListenServer(connections)
    interaction = Interaction(connections, server)

    server_thread = threading.Thread(target=server.listen)
    interaction_thread = threading.Thread(target=interaction.get_command)

    server_thread.start()
    interaction_thread.start()
    
    server_thread.join()
    interaction_thread.join()


if __name__ == "__main__":
    main()