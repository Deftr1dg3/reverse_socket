## Purpose of the Application

The application was created solely for personal enjoyment and for controlling my private PCs remotely over the wide-area network (WAN) using an "ngrok" tunnel. 

## It is in no way intended for illegal activities.

For a more secure connection and file transfer, it is recommended to use the "ssh" utility for connecting to the PCs and the "scp" utility for downloading or uploading files and folders.

## Main Functionality

The main PC acts as the server, accepting and managing connections from the client sockets running in the background on the child PCs. Multiple child PCs can connect to the server simultaneously, without any limit on the number of connections.

The application allows switching between connected child PCs, running Command Line Interface (CLI) commands, and performing real-time file and folder downloads and uploads. For more information, use the "-h" or "--help" options.

If a child PC becomes disconnected, an exception will occur on the server, and the connection will be removed from the list of active connections. The server will automatically disconnect in such cases.

If the server disconnects, the client sockets on the child PCs will attempt to reconnect to the server every "TIMEOUT" period (in seconds), which can be set in the "client/main.py" module.

## Important Note:

The application does not support CLIs that run in real time without providing immediate output. For example, CLIs like vim, nvim, python, node, etc. Using these CLIs will cause the server to become stuck waiting for a response that will never be received. In such cases, the recommended solution is to restart the server.

## This is the most base implementation.

This application creates a reversed socket on the target PC. The socket connects to a host:port, which needs to be provided when creating the ListenServer(connections, host, port) object. Use the address of your Virtual Private Server (VPS) or the address of the "ngrok" tunnel on your PC as the host. The port should be set to 80 or 8080 so that the client PC perceives it as a regular HTTP server and antivirus software does not interfere. The socket runs in the background, continuously waiting for the server to appear on the network as long as the PC is turned on. If you want the script to run in the background indefinitely, you should configure it to start along with the PC.

## Additional Considerations:

1. RSA encryption could be added to every packet sent between machines in the "handle_files.py" module. In this case, key exchange should be performed when a new client is connected in the "listen_server.py" module. Additionally, an additional dictionary called "Keys" should be added to the "Connections" object, which will store the client's IP as the key and the client's Public RSA key as the value. The same approach could be applied to "commands" and "responses."

2. Refactoring should be done to improve code organization. Some method implementations, such as "_create_packet()" and "_send_packet()", in the "execute.py" module should be moved to "handle_files.py". Similarly, certain methods in the "command.py" module should be moved to "execute.py" to enhance code clarity.

3. A notification method could be added to inform all clients when the server has been disconnected (optional).

4. For ease of use and increased robustness, a "remove_client" method could be implemented. This method would store removed clients in a separate set in the "Connections" object and prevent them from reconnecting to the server.

5. Different behavior can be implemented for different kinds of Exceptions.
Meanwhyle it just returns the error message.

6. Additionally, a "restart_clients_socket" method can be added to improve robustness.