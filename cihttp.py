# Neil Marcellini
# 4/12/21
# COMP 429

# Project 2 - A Simple HTTP server.

import socket, logging, threading, json, os.path
import datetime, time
# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)


class HttpRequest():
    def __init__(self, requeststr):
        self.rstr = requeststr
        self.rjson = {}
        self.parse_string()


    def parse_string(self):
        lines = self.rstr.splitlines()
        request_line = lines.pop(0)
        blank_line_index = lines.index('')
        headers = lines[:blank_line_index]
        body = ''
        if blank_line_index + 1 < len(lines):
            body = lines[blank_line_index + 1:]
        self.request_object = {
            "request-line": request_line,
            "headers": headers,
            "body": body,
        }
        self.rjson = json.dumps(self.request_object, indent=4)



    def display_request(self):
        print(self.rjson)

class HttpResponse():
    def __init__(self, request):
        self.request = request
        self.http_version = "HTTP/1.1"
        self.server = "cihttp"
        self.base_path = 'www/'
    
    def response(self):
        request_line = self.request.request_object["request-line"]
        request_words = request_line.split()
        method = request_words.pop(0)
        request_uri = request_words.pop(0)
        file_bytes = self.read_file(request_uri)
        resource_exists = file_bytes is not None
        if not resource_exists:
            self.error_response()
            return
        if method == "HEAD":
            self.head_response(file_bytes)
        elif method == "GET":
            return self.get_response(file_bytes)
        elif method == "POST":
            self.post_response()
        else:
            self.error_response()
    
    def head_response(self, file_bytes):
        status_code = 200
        reason_pharse = "OK"
        content_len = len(file_bytes)
        print(f"content_len = {content_len}")
        pass

    def get_response(self, file_bytes):
        status_code = "200"
        reason_pharse = "OK"
        status_line = " ".join([self.http_version, status_code, reason_pharse])
        content_len = len(file_bytes)
        content_len_header = f"Content-Length: {content_len}"
        server_header = f"Server: {self.server}"
        print(f"content_len = {content_len}")
        last_modified_header = self.last_modified()
        body = file_bytes
        response_str = "\r\n".join([status_line, content_len_header, server_header, last_modified_header, "", body])
        response = bytes(response_str, 'utf-8')
        print("response bytes")
        print(response)
        return response

    def post_response(self):
        pass

    def error_response(self):
        status_line = " ".join([self.http_version, "404", "Not Found"])
        pass

    def read_file(self, request_uri):
        # look for the file at the given uri
        self.file_path = self.base_path + request_uri
        file_exists = os.path.isfile(self.file_path)
        if not file_exists:
            return None
        # open the file and return the bytes
        with open(self.file_path) as f:
            data = f.read()
            return data
    
    def last_modified(self):
        # return the last modified time of the file
        modified_time = os.path.getmtime(self.file_path)
        utc_datetime = datetime.datetime.utcfromtimestamp(modified_time)
        time_str = utc_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
        last_modified = f"Last-Modified: {time_str}"
        print(last_modified)
        return last_modified


        



class ClientThread(threading.Thread):
    def __init__(self, address, socket):
        threading.Thread.__init__(self)
        self.csock = socket
        logging.info('New connection added.')


    def run(self):
        # exchange messages
        request = self.csock.recv(1024)
        req = request.decode('utf-8')
        logging.info('Recieved a request from client: ' + req)

        httpreq = HttpRequest(req)

        httpreq.display_request()

        http_res = HttpResponse(httpreq)
        response = http_res.response()

        # send a response
        #self.csock.send(b"HTTP/1.1 500 Not a real fake server (yet).\r\nServer: cihttpd\r\n\r\n<html><body><h1>500 Internal Server Error</h1><p>Garbage Tier Server.</p></body></html>")
        self.csock.send(response)

        # disconnect client
        self.csock.close()
        logging.info('Disconnect client.')


def server():
    logging.info('Starting cihttpd...')

    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # client has connected
        sc,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc)
        t.start()


server()