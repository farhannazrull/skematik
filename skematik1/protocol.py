DELIMITER = "|"

# protocol.py
def encode_message(msg_type, payload):
    return f"{msg_type}|{payload}"

def decode_message(message):
    parts = message.split("|", 1)
    return parts[0], parts[1] if len(parts) > 1 else ""