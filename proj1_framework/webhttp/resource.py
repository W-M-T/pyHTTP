"""Resources

This module contains a handler class for resources.
"""

import os
import mimetypes
import hashlib

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class FileExistError(Exception):
    """Exception which is raised when file does not exist"""
    pass


class FileAccessError(Exception):
    """Exception which is raised when file exists, but cannot be accessed"""
    pass


class Resource:
    """Class for representing a Resource (file)"""

    def __init__(self, uri):
        """Initialize the resource"

        Raises:
            FileExistError: if resource does not exist
            FileAccessError: if resource exists, but cannot be accessed

        Args:
            uri (str): Uniform Resource Identifier
        """

        self.uri = uri
        out = urlparse.urlparse(uri)
        self.path = os.path.join("content", out.path.lstrip("/"))
        if os.path.isdir(self.path):
            self.path = os.path.join(self.path, "index.html")
        if not os.path.isfile(self.path):
            raise FileExistError
        if not os.access(self.path, os.R_OK):
            raise FileAccessError

    def generate_etag(self):
        """Generate the ETag for the resource

        Returns:
            str: ETag for the resource
        """
        stat = os.stat(self.path)
        metadata = str(stat.st_ino) + str(stat.st_mtime) + str(stat.st_size)
        
        h = hashlib.sha1()
        h.update(metadata)#.encode()
        etag = str(h.hexdigest())
        
        return etag

    def get_content(self):
        """Get the contents of the resource
        
        Returns:
            str: Contents of the resource
        """
        file = open(self.path)
        str = file.read()
        file.close()
        return str

    def get_content_type(self):
        """Get the content type, i.e "text/html"

        Returns:
            str: type of content in the resource
        """
        mimetype = mimetypes.guess_type(self.path)
        return mimetype[0]

    def get_content_encoding(self):
        """Get the content encoding, i.e "gzip"

        Returns:
            str: encoding used for the resource
        """
        mimetype = mimetypes.guess_type(self.path)
        return mimetype[1]

    def get_content_length(self):
        """Get the length of the resource

        Returns:
            int: length of resource in bytes
        """
        return os.path.getsize(self.path)
