# server.py
import socket
import threading
import random
import time
from protocol import encode_message, decode_message
from emailer import send_winner_email

HOST = "127.0.0.1"
PORT = 65432

clients = {}
scores = {}
emails = {}
current_drawer = None
current_word = ""
word_list = ["kucing", "gedung", "sepeda", "komputer", "ITS", "robot", "cinta", "keyboard"]
lock = threading.Lock()
round_timer = None
round_time_limit = 30  # seconds

def broadcast(msg, exclude=None):
    for user, conn in clients.items():
        if user != exclude:
            try:
                conn.send(msg.encode())
            except:
                pass

def send_scores():
    score_msg = ";".join(f"{user},{score}" for user, score in scores.items())
    broadcast(encode_message("SCORE", score_msg))

def timer_thread(drawer):
    global current_drawer
    for remaining in range(round_time_limit, 0, -1):
        time.sleep(1)
        if current_drawer != drawer:
            return  # round already changed (correct guess)
    # Time's up!
    broadcast(encode_message("MSG", f"⏰ Waktu habis! Jawaban yang benar adalah: {current_word}"))
    next_round()

def start_timer(drawer):
    global round_timer
    if round_timer and round_timer.is_alive():
        return
    round_timer = threading.Thread(target=timer_thread, args=(drawer,), daemon=True)
    round_timer.start()

def next_round():
    global current_drawer, current_word
    users = list(clients.keys())
    if not users:
        return

    if current_drawer is None:
        current_drawer = users[0]
    else:
        idx = users.index(current_drawer)
        current_drawer = users[(idx + 1) % len(users)]

    current_word = random.choice(word_list)
    hint = current_word[0] + "_" * (len(current_word) - 1)

    broadcast(encode_message("WORD", hint))
    broadcast(encode_message("DRAWER", current_drawer))
    clients[current_drawer].send(encode_message("WORD", current_word).encode())

    start_timer(current_drawer)

def handle_client(conn, addr):
    global current_drawer, current_word
    print(f"[NEW CONNECTION] {addr} connected.")

    username, email = None, None
    try:
        join_data = conn.recv(1024).decode()
        msg_type, payload = decode_message(join_data)
        if msg_type == "JOIN":
            username, email = payload.split(",")
            with lock:
                clients[username] = conn
                emails[username] = email
                scores[username] = 0

            print(f"[ACTIVE CONNECTIONS] {len(clients)}")
            broadcast(encode_message("MSG", f"{username} joined the game!"))

            if len(clients) >= 2:
                next_round()

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg_type, payload = decode_message(data)

            if msg_type == "DRAW" and username == current_drawer:
                broadcast(encode_message("DRAW", payload), exclude=username)

            elif msg_type == "GUESS":
                broadcast(encode_message("MSG", f"{username}: {payload}"), exclude=username)
                if payload.lower() == current_word.lower() and username != current_drawer:
                    broadcast(encode_message("CORRECT", username))
                    scores[username] += 10
                    scores[current_drawer] += 5
                    send_scores()
                    send_winner_email(emails[username], username)
                    next_round()

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        if username:
            with lock:
                clients.pop(username, None)
                emails.pop(username, None)
                scores.pop(username, None)
            broadcast(encode_message("MSG", f"{username} left the game."))
            print(f"[DISCONNECT] {addr} disconnected.")

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTING] Server is starting on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start()
