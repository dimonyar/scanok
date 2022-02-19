import hashlib


def str2hash(string):
    result = hashlib.md5(string.encode())

    return result.hexdigest()
