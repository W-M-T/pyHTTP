import unittest
import socket
import sys
import time

import webhttp.message
import webhttp.parser
import webhttp.consts
import webhttp.resource
import webhttp.composer


portnr = 8001


class TestGetRequests(unittest.TestCase):
    """Test cases for GET requests"""

    def setUp(self):
        """Prepare for testing"""
        #print("Hi")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", portnr))
        self.parser = webhttp.parser.ResponseParser()

    def tearDown(self):
        """Clean up after testing"""
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()

    def test_existing_file(self):
        """GET for a single resource that exists"""
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/index.html"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        self.client_socket.send(str(request).encode())

        #Get the resource to compare
        wantedres = webhttp.resource.Resource("/test/index.html")
        
        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, wantedres.get_content())

    def test_nonexistant_file(self):
        """GET for a single resource that does not exist"""
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/nofilewiththisnameright.html"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        self.client_socket.send(str(request).encode())

        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, "404 " + webhttp.consts.REASON_DICT[404])

    def test_caching(self):#IMPLEMENTEER NOG CACHE CORRECTNESS https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html
        """GET for an existing single resource followed by a GET for that same
        resource with caching utilized on the client/tester side
        """
        # Send the first request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/index.html"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")#Dit is geen test van persistence
        self.client_socket.send(str(request).encode())

        # Get the etag
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        etag = response.get_header("ETag")
        #print(etag)

        self.assertEqual(response.code, 200)
        self.assertTrue(response.body)

        # Send the second request
        self.tearDown()
        self.setUp()#Dit is geen test van persistence
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/index.html"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        request.set_header("If-None-Match", etag)
        self.client_socket.send(str(request).encode())

        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 304)
        self.assertFalse(response.body)

    def test_existing_index_file(self):
        """GET for a directory with an existing index.html file"""
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        self.client_socket.send(str(request).encode())

        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 200)
        self.assertTrue(response.body)

    def test_nonexistant_index_file(self):
        """GET for a directory with a non-existant index.html file"""
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/testnoindex/"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        self.client_socket.send(str(request).encode())

        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 404)
        self.assertEqual(response.body, "404 " + webhttp.consts.REASON_DICT[404])

    def test_persistent_close(self):
        """Multiple GETs over the same (persistent) connection with the last
        GET prompting closing the connection, the connection should be closed.
        """
        pass

    def test_persistent_timeout(self):
        """Multiple GETs over the same (persistent) connection, followed by a
        wait during which the connection times out, the connection should be
        closed.
        """
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/shuckle.jpg"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "keep-alive")#Not even necessary, same effect as nothing in the rfc
        self.client_socket.send(str(request).encode())


        # Remove the response from the buffer
        message = self.client_socket.recv(1024)

        # Test if the connection is still alive
        self.client_socket.send(str(request).encode())
        message = self.client_socket.recv(1024)
        self.assertTrue(message)

        #Wait
        time.sleep(16)

        # Test if the connection is still alive
        self.client_socket.send(str(request).encode())
        message = self.client_socket.recv(1024)
        self.assertFalse(message)

        #Restart connection, just to prevent tearDown from throwing an exception
        self.setUp()

    def test_encoding(self):
        """GET which requests an existing resource using gzip encoding, which
        is accepted by the server.
        """
        # Send the request
        request = webhttp.message.Request()
        request.method = "GET"
        request.uri = "/test/"
        request.set_header("Host", "localhost:{}".format(portnr))
        request.set_header("Connection", "close")
        request.set_header("Accept-Encoding", "gzip")
        self.client_socket.send(str(request).encode())

        #Get the resource to compare
        wantedres = webhttp.resource.Resource("/test/index.html")

        # Test response
        message = self.client_socket.recv(1024)
        response = self.parser.parse_response(message)
        self.assertEqual(response.code, 200)
        self.assertEqual(response.get_header("Content-Encoding"), "gzip")

        #Compare the decompressed data with the original data
        decoded = webhttp.composer.gzip_decode(response.body)
        self.assertEquals(wantedres.get_content(), decoded)


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="HTTP Tests")
    parser.add_argument("-p", "--port", type=int, default=8001)
    
    # Arguments for the unittest framework
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    
    # Only pass the unittest arguments to unittest
    sys.argv[1:] = args.unittest_args

    # Start test suite
    unittest.main()
