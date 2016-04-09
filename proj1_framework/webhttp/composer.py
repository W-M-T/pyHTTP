""" Composer for HTTP responses

This module contains a composer, which can compose responses to
HTTP requests from a client.
"""

import time

import webhttp.message
import webhttp.resource
import webhttp.consts
import gzip
try:
    import StringIO as sIO
except ImportError:
    import io as sIO
import sys



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
        print(request.uri)
        if request.version != "HTTP/1.1":
            response.code = 505
            response.body = "Please upgrade your browser to support HTTP/1.1!"
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

                        #TODO check via resource.get_encoding of het al geencode is en stuur het mee
                        #Zoek ook uit wat er moet gebeuren als accept-encoding/accept-charset/accept niet matcht
                        if encoding_acceptable(request.get_header("Accept-Encoding"), "gzip") and sys.version_info < (3,0):#Geen gzip voor python 3
                            response.body = gzip_encode(resource.get_content())
                            response.set_header("Content-Encoding", "gzip")
                        else:
                            if encoding_acceptable(request.get_header("Accept-Encoding"), "identity"):
                                response.body = resource.get_content()
                            else:
                                print("CLIENT DOESNT ACCEPT KNOWN ENCODING")
                                response.code = 406
                                errmsg = "406 " + webhttp.consts.REASON_DICT[406]
                                response.body = errmsg
                                response.set_header("Content-Length", len(errmsg))
                                response.set_header("Content-Type", "text/html; charset=UTF-8")
                            
                        print("Content: ")
                        print(response.body)
                        
                        response.set_header("Content-Length", len(resource.get_content()))
                        response.set_header("ETag", etag)

                except webhttp.resource.FileExistError:
                    print("FILE DOESNT EXIST")
                    response.code = 404
                    errmsg = "404 " + webhttp.consts.REASON_DICT[404]
                    response.body = errmsg
                    response.set_header("Content-Length", len(errmsg))
                    response.set_header("Content-Type", "text/html; charset=UTF-8")
                                        
                except webhttp.resource.FileAccessError:
                    print("FILE ACCESS WENT WRONG")
                    response.code = 500
                    errmsg = "500 " + webhttp.consts.REASON_DICT[500]
                    response.body = errmsg
                    response.set_header("Content-Length", len(errmsg))
                    response.set_header("Content-Type", "text/html; charset=UTF-8")

            
                
        # Stub code
        #response.set_header("Content-Length", 0)
        #response.set_header("Connection", "close")
        #set datetime
        response.set_header("Date", self.make_date_string())
        print(response)
        return response

    def make_date_string(self):
        """Make string of date and time
        
        Returns:
            str: formatted string of date and time
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

def gzip_encode(s):
    out = sIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as inp:
        inp.write(s)
    return out.getvalue()

def gzip_decode(s):
    out = sIO.StringIO(s)
    string = gzip.GzipFile('', 'r', 0, sIO.StringIO(s)).read()
    with gzip.GzipFile(fileobj=out, mode="r") as inp:
        #string = inp.read()
        pass
    return string

def encoding_acceptable(header, enc):
    """Check if the Accept-Encoding header states that gzip is acceptable

    Returns:
        bool: True if gzip is acceptable; False otherwise
    """
    encodings = header.split(",")
    if encodings != ['']:
        for encoding in encodings:
            if enc in encoding or (enc not in encoding and "*" in encoding):
                    parts = encoding.split(";")
                    if len(parts) == 1:
                        return True;
                    else:
                        qval = parts[1].replace("q=", "", 1).strip()
                        try:
                            return (float(qval) > 0)
                        except:
                            return False;
    return enc == "identity"
