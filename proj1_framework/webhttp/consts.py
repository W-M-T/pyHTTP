GENERAL_HEADERS = ["Cache-Control", "Connection", "Date", "Pragma", "Trailer", "Transfer-encoding",
 "Upgrade", "Via", "Warning"]

REQUEST_HEADERS = ["Accept", "Accept-Charset", "Accept-Encoding", "Accept-Language", "Authorization","DNT",
 "Expect", "From", "Host", "If-Match", "If-Modified-Since", "If-None-Match", "If-Range",
 "If-Unmodified-Since", "Max-Forwards", "Proxy-Authorization", "Range", "Referer", "TE", "User-Agent"]

RESPONSE_HEADERS = ["Accept-Ranges", "Age", "ETag", "Location", "Proxy-Authenticate", "Retry-After",
"Server", "Vary", "WWW-Authenticate"]

ENTITY_HEADERS = ["Allow", "Content-Encoding", "Content-Language", "Content-Length", "Content-Location",
"Content-MD5", "Content-Range", "Content-Type", "Expires", "Last-Modified"]

REASON_DICT = {
    # Dictionary for code reasons
    # Format: code : "Reason"
    100 : "Continue",
    101 : "Switching Protocols",
    200 : "OK",
    201 : "Created",
    202 : "Accepted",
    203 : "Non-Authorative Information",
    204 : "No Content",
    205 : "Reset Content",
    206 : "Partial Content",
    301 : "Moved Permanently",
    302 : "Found",
    303 : "See Other",
    304 : "Not Modified",
    305 : "Use Proxy",
    307 : "Temporary Redirect",
    400 : "Bad Request",
    401 : "Unauthorized",
    402 : "Payment Required",
    403 : "Forbidden",
    404 : "Not Found",
    406 : "Not Acceptable",
    412 : "Precondition Failed",
    418 : "I'm a teapot",
    500 : "Internal Server Error",
    501 : "Not implemented",
    502 : "Bad Gateway",
    503 : "Service Unavailable",
    504 : "Gateway Time-out",
    505 : "HTTP Version not supported"
}
