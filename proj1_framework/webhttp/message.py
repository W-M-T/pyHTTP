"""HTTP Messages

This modules contains classes for representing HTTP responses and requests.
"""

import webhttp.consts as consts

reasondict = {
    # Dictionary for code reasons
    # Format: code : "Reason"
    200 : "OK",
    301 : "Moved Permanently",
    302 : "Moved Temporarily",
    304 : "Not modified",
    400 : "Bad Request",
    401 : "Unauthorized",
    403 : "Forbidden",
    404 : "Not Found",
    500 : "Internal Server Error",
    503 : "Service Unavailable"
}


class Message(object):
    """Class that stores a HTTP Message"""

    def __init__(self):
        """Initialize the Message"""
        self.version = "HTTP/1.1"
        self.startline = ""
        self.body = ""
        self.headerdict = dict()
        
    def set_header(self, name, value):
        """Add a header and its value
        
        Args:
            name (str): name of header
            value (str): value of header
        """
        self.headerdict[name] = value
        
    def get_header(self, name):
        """Get the value of a header
        
        Args:
            name (str): name of header

        Returns:
            str: value of header, empty if header does not exist
        """
        if name in self.headerdict:
            return self.headerdict[name]
        else:
            return ""
        
    def __str__(self):
        """Convert the Message to a string
        
        Returns:
            str: representation the can be sent over socket
        """

        header = ""

        headernames = consts.generalheaders + consts.requestheaders + consts.responseheaders + consts.entityheaders 

        for name in headernames:
            if self.get_header(name) != "":
                header += name + ": " + self.get_header(name) + "\r\n"

        return header + "\r\n" + self.body


class Request(Message):
    """Class that stores a HTTP request"""

    def __init__(self):
        """Initialize the Request"""
        super(Request, self).__init__()
        self.method = ""
        self.uri = ""
        
    def __str__(self):
        """Convert the Request to a string

        [method] [URL] [version]
        [headers]
        [body]

        Returns:
            str: representation the can be sent over socket
        """
        self.startline = self.method + " " + self.uri + " " + self.version
        return self.startline + "\r\n" + super(Request, self).__str__()
        

class Response(Message):
    """Class that stores a HTTP Response"""

    def __init__(self):
        """Initialize the Response"""
        super(Response, self).__init__()
        self.code = 500
    
    def __str__(self):
        """Convert the Response to a string

        [version] [status] [reason]
        [headers]
        [body]

        Returns:
            str: representation the can be sent over socket
        """
        self.startline = self.version + " " + str(self.code) + " " + reasondict[self.code]             
        return self.startline + "\r\n" + super(Response, self).__str__()
