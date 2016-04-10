"""HTTP Server

This module contains a HTTP server
"""

import threading
import time
import socket
import select
import platform
from webhttp import parser
from webhttp import composer

class ConnectionHandler(threading.Thread):
    """Connection Handler for HTTP Server"""
 
    def __init__(self, conn_socket, addr, timeout, rqparser, rspcomposer):
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
        self.rspcomposer = rspcomposer
    
    def handle_connection(self):#Op het moment nog geen persistence/pipelining
        """Handle a new connection"""
        print("[+] - Handling new connection")
        self.conn_socket.settimeout(self.timeout)
        sock_open = True
        while sock_open:
            try:
                print("[+] - Ready to receive request.")
                buf = self.conn_socket.recv(4096)
                if not buf:
                    print("[-] - Connection was reset.")
                    break
                print(self.conn_socket.gettimeout())
                #print(buf)
                parsed_requests = self.rqparser.parse_requests(buf)
                for request in parsed_requests:
                    if sock_open:
                        print("[*] - Result after parsing:\n")
                        print(request)
                        print(request.get_header("Connection"))
                        if request.get_header("Connection") == "close":
                            print("[+] - Closing socket because requested.")
                            sock_open = False
                        print("[*] - Finding response.")
                        response = self.rspcomposer.compose_response(request)
                        print("[+] - Composed response.")
                        print(response)
                        print("[*] - Sending response.")
                        self.conn_socket.send(str(response))
                        print("[+] - Response sent.")
            except (socket.timeout, socket.error):
                print("[-] - Socket timed out.")
                break
                
        print("[*] - Closing socket")
        self.conn_socket.shutdown(socket.SHUT_RDWR)
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
        self.rqparser = parser.RequestParser()
        self.rspcomposer = composer.ResponseComposer(timeout)
        
        self.connlist = []

    def acceptcon(self, s):
        (client_socket, address) = s.accept()
        
        ch = ConnectionHandler(client_socket, address, self.timeout, self.rqparser, self.rspcomposer)
        self.connlist.append(ch)
        ch.run()
        
    def run(self):
        """Run the HTTP Server and start listening"""
        #socket.settimeout(timeout)
        print("[+] - Server up and running.")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Allows sockets to be re-used right away and fixes the "Address still in use" error
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((self.hostname, self.server_port))#try catch enzo nog
        s.listen(10)#parameter maken?

        if platform.system() == 'Windows':
            s.settimeout(1)
            while not self.done:
                try:
                    self.acceptcon(s)
                except (OSError, socket.timeout):#BlockingIOError
                    pass
        else:
            while not self.done:
                self.acceptcon(s)
    
    def shutdown(self):
        """Safely shut down the HTTP server"""
        #Ook connection handlers beeindigen?
        #for ch in self.connlist:
        #    ch.exit()
        self.done = True
