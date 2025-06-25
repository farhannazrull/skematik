# gui.py
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import socket
import threading
from protocol import encode_message, decode_message

HOST = "127.0.0.1"
PORT = 65432

class GameClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Skematik - Guess The Drawing")
        self.root.geometry("900x650")
        self.username = ""
        self.email = ""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.setup_login()

    def setup_login(self):
        self.login_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="👤 Username", font=("Segoe UI", 16), bg="#f0f0f0").pack(pady=10)
        self.username_entry = tk.Entry(self.login_frame, font=("Segoe UI", 16), width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self.login_frame, text="✉️ Email", font=("Segoe UI", 16), bg="#f0f0f0").pack(pady=10)
        self.email_entry = tk.Entry(self.login_frame, font=("Segoe UI", 16), width=30)
        self.email_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Gabung", font=("Segoe UI", 16, "bold"), bg="#4CAF50", fg="white",
                  padx=20, pady=5, command=self.connect).pack(pady=20)

    def connect(self):
        self.username = self.username_entry.get().strip()
        self.email = self.email_entry.get().strip()
        if not self.username or not self.email:
            messagebox.showerror("Error", "Lengkapi username dan email.")
            return
        try:
            self.sock.connect((HOST, PORT))
            self.sock.send(encode_message("JOIN", f"{self.username},{self.email}").encode())
            self.login_frame.destroy()
            self.setup_game_ui()
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def setup_game_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = tk.Label(top_frame, text="Menunggu pemain lain...", font=("Segoe UI", 14), anchor="w")
        self.status_label.pack(side=tk.LEFT)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(main_frame, bg="white", width=600, height=400, relief=tk.RIDGE, bd=2)
        self.canvas.grid(row=0, column=0, rowspan=3, padx=5, pady=5)
        self.canvas.bind("<B1-Motion>", self.draw)

        self.chat_box = scrolledtext.ScrolledText(main_frame, state="disabled", width=35, height=20)
        self.chat_box.grid(row=0, column=1, padx=5, pady=5)

        self.guess_entry = tk.Entry(main_frame, font=("Segoe UI", 14))
        self.guess_entry.grid(row=1, column=1, padx=5, sticky="ew")
        self.guess_entry.bind("<Return>", self.send_guess)

    def draw(self, event):
        try:
            x, y = event.x, event.y
            self.canvas.create_oval(x, y, x+3, y+3, fill="black")
            self.sock.send(encode_message("DRAW", f"{x},{y}").encode())
        except:
            pass

    def send_guess(self, event):
        guess = self.guess_entry.get().strip()
        if guess:
            self.sock.send(encode_message("GUESS", guess).encode())
            self.guess_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break
                msg_type, payload = decode_message(data)
                if msg_type == "MSG":
                    self.append_chat(payload)
                elif msg_type == "DRAW":
                    x, y = map(int, payload.split(","))
                    self.canvas.create_oval(x, y, x+3, y+3, fill="black")
                elif msg_type == "WORD":
                    self.status_label.config(text=f"🔤 Tebak Kata: {payload}")
                elif msg_type == "DRAWER":
                    self.append_chat(f"🖌️ {payload} sedang menggambar")
                elif msg_type == "CORRECT":
                    self.append_chat(f"✅ {payload} menebak dengan benar!")
                elif msg_type == "SCORE":
                    scores = [f"{u}: {s}" for u, s in [x.split(",") for x in payload.split(";")]]
                    self.append_chat("🏆 Skor:")
                    for s in scores:
                        self.append_chat(" - " + s)
            except:
                break

    def append_chat(self, msg):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, msg + "\n")
        self.chat_box.config(state="disabled")
        self.chat_box.see(tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    GameClient().run()