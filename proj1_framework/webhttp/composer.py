""" Composer for HTTP responses

This module contains a composer, which can compose responses to
HTTP requests from a client.
"""

import time

import webhttp.message
import webhttp.resource
import webhttp.consts
import gzip


class ResponseComposer:
    """Class that composes a HTTP response to a HTTP request"""

    def __init__(self, timeout):
        """Initialize the ResponseComposer
        
        Args:
            timeout (int): connection timeout
        """
        self.timeout = timeout
    
    def compose_response(self, request):
        """Compose a response to a request
        
        Args:
            request (webhttp.Request): request from client

        Returns:
            webhttp.Response: response to request

        """
        response = webhttp.message.Response()
        #print("Hi")
        print(request.uri)
        if request.version != "HTTP/1.1":
            response.code = 505
        else:
            if request.method == "GET":
                try:#Gebruik de header "Accept" uit de request nog
                    resource = webhttp.resource.Resource(request.uri)
                    response.code = 200
                    response.set_header("Content-Type", resource.get_content_type())
                    #compressed = self.gzip_encode(resource.get_content())
                    #response.body = compressed
                    response.body = resource.get_content()
                    #response.set_header("Content-Length", len(compressed))
                    response.set_header("Content-Length", len(resource.get_content()))
                    #response.set_header("Content-Encoding", "gzip")
                    print(resource.get_content())
                                        
                except webhttp.resource.FileExistError:
                    print("FILE DOESNT EXIST")
                    response.code = 404
                    errmsg = "404 " + webhttp.consts.REASON_DICT[404]
                    #response.body = errmsg
                    response.set_header("Content-Length", len(errmsg))
                    response.set_header("Content-Type", "text/html; charset=UTF-8")
                                        
                except webhttp.resource.FileAccessError:
                    print("FILE ACCESS WENT WRONG")
                    response.code = 500
                    errmsg = "500 " + webhttp.consts.REASON_DICT[500]
                    response.set_header("Content-Length", len(errmsg))
                    response.set_header("Content-Type", "text/html; charset=UTF-8")

            
                
        # Stub code
        #response.set_header("Content-Length", 0)
        #response.set_header("Connection", "close")
        #set datetime
        #response.body = "Test"
        print(response)
        return response

    def gzip_encode(self, string):
        sbytes = gzip.compress(bytes(string, 'utf-8'))
        s_out = sbytes.decode(encoding='utf-8')

    def make_date_string(self):
        """Make string of date and time
        
        Returns:
            str: formatted string of date and time
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
