"""HTTP Server

This module contains a HTTP server
"""

import threading
import socket


class ConnectionHandler(threading.Thread):
    """Connection Handler for HTTP Server"""

    def __init__(self, conn_socket, addr, timeout):
        """Initialize the HTTP Connection Handler
        
        Args:
            conn_socket (socket): socket used for connection with client
            addr (str): ip address of client
            timeout (int): seconds until timeout
        """
        super(ConnectionHandler, self).__init__()
        self.daemon = True
        self.conn_socket = conn_socket
        self.addr = addr
        self.timeout = timeout
    
    def handle_connection(self):
        """Handle a new connection"""
        print("Hi")
        conn_socket.recv(4096)
        conn_socket.send("Hello world!")
        conn_socket.close()
        
    def run(self):
        """Run the thread of the connection handler"""
        self.handle_connection()
        

class Server:
    """HTTP Server"""

    def __init__(self, hostname, server_port, timeout):
        """Initialize the HTTP server
        
        Args:
            hostname (str): hostname of the server
            server_port (int): port that the server is listening on
            timeout (int): seconds until timeout
        """
        self.hostname = hostname
        self.server_port = server_port
        self.timeout = timeout
        self.done = False
        
        self.connlist = []
    
    def run(self):
        """Run the HTTP Server and start listening"""
        #socket.settimeout(timeout)
        print("server hello")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.hostname, self.server_port))#try catch enzo nog
        s.listen(10)#parameter maken?
        
        while not self.done:
            (client_socket, address) = s.accept()
            ch = ConnectionHandler(client_socket, adress, self.timeout)
            self.connlist.append(ch)
            ch.run()
    
    def shutdown(self):
        """Safely shut down the HTTP server"""
        #Ook connection handlers beeindigen?
        for ch in self.connlist:#niet hoe het hoort
            ch.exit()
        self.done = True
