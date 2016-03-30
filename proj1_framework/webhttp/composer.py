""" Composer for HTTP responses

This module contains a composer, which can compose responses to
HTTP requests from a client.
"""

import time

import webhttp.message
import webhttp.resource
import webhttp.consts
import gzip
import StringIO


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
                    etag = resource.generate_etag()
                    if etag == request.get_header("If-None-Match"):
                        response.code = 304
                    else:
                        response.set_header("Content-Type", resource.get_content_type())
                        #compressed = self.gzip_encode(resource.get_content())
                        #response.body = compressed
                        print("Content: ")
                        print(resource.get_content())
                        response.body = resource.get_content()
                        #TODO: checken of hij zegt dat hij gzip wil of dat hij hem juist absoluut niet wil
                        if "gzip" in request.get_header("Accept-Encoding"):
                            print("Encoding with gzip")
                            response.body = self.gzip_encode(response.body)
                        #print("Encoding with gzip")
                        self.gzip_encode(response.body)
                        #response.set_header("Content-Length", len(compressed))
                        response.set_header("Content-Length", len(resource.get_content()))
                        response.set_header("Content-Encoding", "gzip")
                        response.set_header("ETag", etag)
                        #print(resource.get_content())

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

    def gzip_encode(self, s):
        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as inp:
            inp.write(s)
        return out.getvalue()


    def make_date_string(self):
        """Make string of date and time
        
        Returns:
            str: formatted string of date and time
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
