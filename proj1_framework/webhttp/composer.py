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
                    print(request)
                    print(request.get_header("If-None-Match"))
                    print(etag)

                    if request.get_header("If-Match") != "" and \
                    not match_etag(request.get_header("If-Match"), etag):
                        response.code = 412
                    if match_etag(request.get_header("If-None-Match"), etag):
                        response.code = 304
                    else:
                        #We need to send a response with a body

                        #Set standard headers for responses that have a resource
                        response.set_header("Content-Type", resource.get_content_type())
                        response.set_header("ETag", "\"" + etag + "\"")#rfc
                        response.set_header("Last-Modified", resource.get_last_modified())

                        
                        if encoding_acceptable(request.get_header("Accept-Encoding"), "gzip") and sys.version_info < (3,0):#Geen gzip voor python 3
                            #Gzip is acceptable
                            
                            if resource.get_content_encoding() != 'gzip':
                                #The resource is not encoded yet
                                response.body = gzip_encode(resource.get_content())
                            else:
                                #The resource is already encoded
                                response.body = resource.get_content()
                                
                            response.set_header("Content-Encoding", "gzip")
                            
                            
                        elif encoding_acceptable(request.get_header("Accept-Encoding"), "identity"):
                            #Gzip is not acceptable, but identity is
                            
                            #print(len(resource.get_content()))The same in linux, not the same in windows
                            #print(resource.get_content_length())
                            response.body = resource.get_content()
                        else:
                            #No encoding we support is accepted
                            
                            print("[-] - Client doesn't accept any known encoding.")
                            response.code = 406
                            errmsg = "406 " + webhttp.consts.REASON_DICT[406]
                            response.body = errmsg
                            response.set_header("Content-Type", "text/html; charset=UTF-8")
                            
                        #print("[*] - Response content: ")
                        #print(response.body)

                except webhttp.resource.FileExistError:
                    print("[-] - File doesn't exist.")
                    response.code = 404
                    errmsg = "404 " + webhttp.consts.REASON_DICT[404]
                    response.body = errmsg
                    response.set_header("Content-Type", "text/html; charset=UTF-8")
                                        
                except webhttp.resource.FileAccessError:
                    print("[-] - Failed to access file.")
                    response.code = 500
                    errmsg = "500 " + webhttp.consts.REASON_DICT[500]
                    response.body = errmsg
                    response.set_header("Content-Type", "text/html; charset=UTF-8")

        #Set the date header and content length
        response.set_header("Date", self.make_date_string())
        response.set_header("Content-Length", len(response.body))
        return response

    def make_date_string(self):
        """Make string of date and time
        
        Returns:
            str: formatted string of date and time
        """
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

def gzip_encode(s):
    out = sIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as inp:
        inp.write(s)
    return out.getvalue()

def gzip_decode(s):
    out = sIO.StringIO(s)
    string = gzip.GzipFile('', 'r', 0, sIO.StringIO(s)).read()
    return string

def decodeTime(timestring):
    eut.parsedate(timestring)

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

def match_etag(tags_in_header, etag):
    taglist = [tag.strip()[1:-1] for tag in tags_in_header.split(',')]
    for tag in taglist:
        if tag == etag:
            return True
    return False
