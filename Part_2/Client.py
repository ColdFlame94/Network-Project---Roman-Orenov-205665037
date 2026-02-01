import socket
import threading
import sys
from Comm import send_data, receive_data

SERVER_HOST_ADDR = "127.0.0.1"
SERVER_PORT_NUM = 5000

def receiver(conn: socket.socket, stop_event: threading.Event):
    try:
        while not stop_event.is_set():
            msg = receive_data(conn)
            print(f"\n{msg}\n> ", end="", flush=True)
    except Exception as e:
        print(f"Error: {e}")

def main():
    host_addr = SERVER_HOST_ADDR
    port_addr = SERVER_PORT_NUM

    if len(sys.argv) >= 2:
        host_addr = sys.argv[1]
    if len(sys.argv) >= 3:
        port_addr = int(sys.argv[2])

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host_addr, port_addr))
    print(f"[CLIENT] Connected to {host_addr}:{port_addr}")

    stop_event = threading.Event()
    t = threading.Thread(
        target=receiver,
        args=(conn, stop_event)
    )
    t.start()

    print("Type commands. First: REGISTER <name>")
    print("> ", end="", flush=True)

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                print("> ", end="", flush=True)
                continue

            send_data(conn, line)

            if line.upper() == "QUIT":
                if t is not None:
                    stop_event.set()
                    t.join(timeout=10)
                break

            print("> ", end="", flush=True)

    except KeyboardInterrupt:
        try:
            send_data(conn, "QUIT")
        except Exception as e:
            print(f"Error: {e}")

    finally:
       try:
           conn.close()
       except Exception as e:
           print(f"{e}")

if __name__ == "__main__":
    main()
