import socket
import threading
from database import Database, ClientInfo
from logger import ChatLogger
from Comm import send_data, receive_data

HOST_ADDR = "127.0.0.1"
PORT_NUM = 5000

db = Database()
lock = threading.Lock()

logger = ChatLogger()

def secure_send(name: str, msg: str):
    with lock:
        client = db.get_client(name)
        if not client:
            return
        conn = client.conn
    try:
        send_data(conn, msg)
    except Exception as e:
        print(f"Error: {e}")

def disconnect(name: str):
    with lock:
        partner = db.get_partner(name)
        db.end_chat(name)
        client = db.get_client(name)
        db.remove_client(name)

    if partner:
        secure_send(partner, f"INFO {name} disconnected. Chat ended.")

    if client:
        try:
            client.conn.close()
        except Exception as e:
            print(f"Error: {e}")

#  Client handler
def handle_client(conn: socket.socket, addr):
    name = None
    try:
        send_data(conn, "INFO Welcome! Please REGISTER <name>")

        while True:
            line = receive_data(conn).strip()
            if not line:
                continue

            cmd, *rest = line.split(" ", 1)
            cmd = cmd.upper()
            arg = rest[0] if rest else ""

            #  Clients' Registration
            if name is None:
                if cmd != "REGISTER":
                    send_data(conn, "ERR You must REGISTER first")
                    continue

                proposed = arg.strip()
                if not proposed:
                    send_data(conn, "ERR Name cannot be empty")
                    continue

                with lock:
                    if db.client_exists(proposed):
                        send_data(conn, "ERR Name already in use")
                        continue
                    name = proposed
                    db.add_client(ClientInfo(conn, addr, name))

                print(f"INFO {name} registered")
                send_data(conn, f"OK REGISTERED {name}")
                send_data(conn, "INFO Commands: CHAT <name> | MSG <text> | END | LIST | QUIT")
                continue

            #  CHAT Commands handler
            match cmd:
                case "LIST":
                    with lock:
                        users = ", ".join(db.list_clients())
                    send_data(conn, f"OK ONLINE {users}")

                case "CHAT":
                    target = arg.strip()
                    with lock:
                        if not db.client_exists(target):
                            send_data(conn, "ERR Target not online")
                            continue
                        if db.get_partner(name) is not None:
                            send_data(conn, "ERR You are already in a chat")
                            continue
                        if db.get_partner(target) is not None:
                            send_data(conn, "ERR Target is busy")
                            continue
                        print(f"INFO {name} chating")
                        db.start_chat(name, target)

                    secure_send(target, f"INFO {name} started a chat with you")
                    send_data(conn, f"OK CHATTING_WITH {target}")

                case "MSG":
                    partner = db.get_partner(name)
                    if not partner:
                        send_data(conn, "ERR You are not in a chat")
                        continue
                    # log message to CSV
                    print(f"INFO {name} sending message")
                    logger.log_message(name, arg)
                    secure_send(partner, f"FROM {name} {arg}")
                    send_data(conn, "OK SENT")

                case "END":
                    print(f"INFO {name} ended")
                    partner = db.get_partner(name)
                    with lock:
                        db.end_chat(name)
                    if partner:
                        secure_send(partner, f"INFO {name} ended the chat")
                    send_data(conn, "OK ENDED")

                case "QUIT":
                    print(f"INFO {name} quit")
                    send_data(conn, "OK BYE")
                    break

                case _:
                    send_data(conn, "ERR Unknown command")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if name:
            disconnect(name)
        else:
            try:
                conn.close()
            except Exception as e:
                print(f"Error: {e}")

#  Main
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST_ADDR, PORT_NUM))
    server.listen(50)

    print(f"SERVER: Listening on {HOST_ADDR}:{PORT_NUM}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()