import socket
import struct

def send_data(conn: socket.socket, text: str) -> None:
    data = text.encode("utf-8")
    header = struct.pack("!I", len(data))
    conn.sendall(header + data)

def receive_bulk(conn: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        bulk = conn.recv(n - len(buf))
        if not bulk:
            raise ConnectionError("Socket closed")
        buf += bulk
    return buf

def receive_data(conn: socket.socket) -> str:
    header = receive_bulk(conn, 4)
    (length,) = struct.unpack("!I", header)
    payload = receive_bulk(conn, length)
    return payload.decode("utf-8", errors="replace")
