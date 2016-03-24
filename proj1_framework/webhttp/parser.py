"""HTTP response and request parsers

This module contains parses for HTTP response and HTTP requests.
"""

import webhttp.message


class RequestParser:
    """Class that parses a HTTP request"""

    def __init__(self):
        """Initialize the RequestParser"""
        pass
        
    def parse_requests(self, buff):
        """Parse requests in a buffer

        Args:
            buff (str): the buffer contents received from socket

        Returns:
            list of webhttp.Request
        """
        requests = self.split_requests(buff.decode())
        http_requests = []
        for request in requests:
            print(request)
            http_request = webhttp.message.Request()
            lines = request.split('\r\n')
            print(lines[0])
            rq = lines[0].split()
            if len(rq) != 3 || rq[2] != "HTTP/1.1":
                pass#Geen geldige request
            else
                http_request.uri = rq[1]
                http_request.method = rq[0]
            lines[0]
            for line in lines[1:]:
                if ':' in line:
                    parts = line.split(":", 1)
                    print (parts)
                    http_request.set_header(parts[0], parts[1])
            http_requests.append(http_request)
        
        return http_requests

    def split_requests(self, buff):
        """Split multiple requests
        
        Arguments:
            buff (str): the buffer contents received from socket

        Returns:
            list of str
        """
        requests = buff.split('\r\n\r\n')
        requests = filter(None, requests)
        requests = [r + '\r\n\r\n' for r in requests]
        requests = [r.lstrip() for r in requests]
        return requests


class ResponseParser:
    """Class that parses a HTTP response"""
    def __init__(self):
        """Initialize the ResponseParser"""
        pass

    def parse_response(self, buff):
        """Parse responses in buffer

        Args:
            buff (str): the buffer contents received from socket

        Returns:
            webhttp.Response
        """
        response = webhttp.message.Response()
        return response
