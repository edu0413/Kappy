from hashlib import sha256

def hash_password(password, salt):
    """
        Use sha256 to hash the password with a salt.
    """
    to_hash = salt + password
    to_hash = to_hash.encode()  # Convert to bytes
    return sha256(to_hash).hexdigest()