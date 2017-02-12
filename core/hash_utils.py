import hashlib


def sha1_file(file_in, chunk_size_kb=512):
    """
    A memory efficient sha1 function for file
    """
    BUF_SIZE = 1024 * chunk_size_kb  # 512 kb per chunk
    hash = hashlib.sha1()

    if hasattr(file_in, 'chunks') and callable(file_in.chunks):
        for chunk in file_in.chunks():
            hash.update(chunk)
    else:
        with open(file_in, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                hash.update(data)

    return hash.hexdigest()
