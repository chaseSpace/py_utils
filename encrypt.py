import hashlib


def md5(msg: str):
    d = hashlib.md5()
    d.update(msg.encode())
    return d.hexdigest()
