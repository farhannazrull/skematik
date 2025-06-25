import socket
import threading
from protocol import encode_message, decode_message

HOST = "127.0.0.1"
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if data:
                msg_type, payload = decode_message(data)
                if msg_type == "DRAW":
                    print("[GAMBAR MASUK] (tidak bisa ditampilkan di terminal)")
                elif msg_type == "MSG":
                    print(payload)
                elif msg_type == "WORD":
                    print(f"[HINT] {payload}")
                elif msg_type == "DRAWER":
                    print(f"[DRAWER] {payload}")
        except:
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    username = input("Enter your username: ")
    email = input("Enter your email (for reward if you win): ")
    join_message = encode_message("JOIN", f"{username},{email}")
    client.send(join_message.encode())

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        msg = input("Guess: ")
        if msg.lower() == "/quit":
            break
        client.send(encode_message("GUESS", msg).encode())

    client.close()

if __name__ == "__main__":
    main()