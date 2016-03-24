"""HTTP Server

This module contains a HTTP server
"""

import threading
import socket
import select
import platform
from webhttp import parser


class ConnectionHandler(threading.Thread):
    """Connection Handler for HTTP Server"""
 
    def __init__(self, conn_socket, addr, timeout, rqparser, composer):
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
        self.rqparser = rqparser
        self.composer = composer
    
    def handle_connection(self):#Op het moment nog geen persistence/pipelining
        conn_socket.settimeout(timeout)
        try:
            """Handle a new connection"""
            print("Handling connection")
            buf = self.conn_socket.recv(4096)
            print("Received input:\n" + str(buf))
            print("Parsing...")
            parsed_requests = self.rqparser.parse_requests(buf)
            print("Parsed requests")
            for request in parsed_requests:
                #check of de header close is
                print("Finding response")
                response = composer.compose_response(request)
                print("Sending response")
                self.conn_socket.send(response.__str__())
                
        except (socket.timeout, socket.error):
            pass
        self.conn_socket.close()#timeout nog regelen
        
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
        self.parser = parser.RequestParser()
        
        self.connlist = []

    def acceptcon(self, s):
        (client_socket, address) = s.accept()
        
        ch = ConnectionHandler(client_socket, address, self.timeout, self.parser)
        self.connlist.append(ch)
        ch.run()
        
    def run(self):
        """Run the HTTP Server and start listening"""
        #socket.settimeout(timeout)
        print("server hello")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.hostname, self.server_port))#try catch enzo nog
        s.listen(10)#parameter maken?

        if platform.system() == 'Windows':
            s.settimeout(1)
            while not self.done:
                try:
                    self.acceptcon(s)
                except (BlockingIOError, socket.timeout):
                    pass
        else:
            self.acceptcon(s)
    
    def shutdown(self):
        """Safely shut down the HTTP server"""
        #Ook connection handlers beeindigen?
        for ch in self.connlist:#niet hoe het hoort
            ch.exit()
        self.done = True
