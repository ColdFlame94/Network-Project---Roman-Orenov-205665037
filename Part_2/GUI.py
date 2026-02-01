import time
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from threading import Event
from Comm import send_data, receive_data

SERVER_HOST_ADDR = "127.0.0.1"
SERVER_PORT_NUM = 5000

#  GUI
class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Chat Client")

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((SERVER_HOST_ADDR, SERVER_PORT_NUM))

        self.stop_event = Event()

        #  Top frame (register/chat)
        top = tk.Frame(root)
        top.pack(padx=10, pady=5)

        tk.Label(top, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(top, width=15)
        self.username_entry.grid(row=0, column=1)

        self.register_btn = tk.Button(top, text="Register", command=self.register)
        self.register_btn.grid(row=0, column=2, padx=5)

        tk.Label(top, text="Chat with:").grid(row=1, column=0)
        self.target_entry = tk.Entry(top, width=15)
        self.target_entry.grid(row=1, column=1)

        self.chat_btn = tk.Button(top, text="Start Chat", command=self.start_chat)
        self.chat_btn.grid(row=1, column=2, padx=5)

        self.end_btn = tk.Button(top, text="End Chat", command=self.end_chat)
        self.end_btn.grid(row=1, column=3, padx=5)

        #  Chat area
        self.text_area = scrolledtext.ScrolledText(root, state="disabled", width=70, height=20)
        self.text_area.pack(padx=10, pady=10)

        #  Bottom frame (message)
        bottom = tk.Frame(root)
        bottom.pack(padx=10, pady=5)

        self.msg_entry = tk.Entry(bottom, width=50)
        self.msg_entry.grid(row=0, column=0, padx=5)
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(bottom, text="Send", command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=5)

        self.quit_btn = tk.Button(bottom, text="Quit", command=self.on_close)
        self.quit_btn.grid(row=0, column=2, padx=5)

        #  Receiver thread
        threading.Thread(target=self.receive_loop, daemon=True).start()

        self.print_msg("Connected to server.")
        self.print_msg("Use buttons to interact.")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    #  UI helpers
    def print_msg(self, msg):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)

    #  Commands
    def register(self):
        name = self.username_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Username required")
            return
        send_data(self.conn, f"REGISTER {name}")

    def start_chat(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Target username required")
            return
        send_data(self.conn, f"CHAT {target}")

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        send_data(self.conn, f"MSG {msg}")
        self.msg_entry.delete(0, tk.END)

    def end_chat(self):
        send_data(self.conn, "END")

    #  Networking
    def receive_loop(self):
        try:
            while not self.stop_event.is_set():
                msg = receive_data(self.conn)
                self.root.after(0, self.print_msg, msg)
        except Exception as e:
            print(f"Error: {e}")

    def on_close(self):
        try:
            send_data(self.conn, "QUIT")
        except Exception as e:
            print(f"Error: {e}")

        self.stop_event.set()
        time.sleep(0.1)

        try:
            self.conn.close()
        except Exception as e:
            print(f"Error: {e}")
        self.root.destroy()

#  Run
if __name__ == "__main__":
    root = tk.Tk()
    ChatClientGUI(root)
    root.mainloop()
