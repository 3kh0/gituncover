import requests
from colorama import Fore
import pgpy

def fetch_ssh(username):
    url = f"https://github.com/{username}.keys"
    try:
        response = requests.get(url)
        response.raise_for_status()
        keys = response.text.strip().split("\n")
        processed_keys = []
        for key in keys:
            if key:
                key_parts = key.split()
                key_type = key_parts[0] if len(key_parts) > 0 else "unknown"
                key_data = key_parts[1] if len(key_parts) > 1 else "unknown"
                comment = key_parts[2] if len(key_parts) > 2 else "no comment"
                processed_keys.append({
                    "type": key_type,
                    "key": key_data,
                    "comment": comment
                })
        return processed_keys
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"error getting ssh keys: {e}")
        return []

def fetch_gpg(username):
    url = f"https://github.com/{username}.gpg"
    try:
        response = requests.get(url)
        response.raise_for_status()
        gpg_key_block = response.text.strip()
        key_metadata = read_gpg(gpg_key_block)
        return {
            "raw_key": gpg_key_block,
            "metadata": key_metadata
        }
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"error getting gpg keys: {e}")
        return {"raw_key": "", "metadata": {}}

def read_gpg(gpg_key_block):
    metadata = {}
    try:
        key, _ = pgpy.PGPKey.from_blob(gpg_key_block)
        if key:
            metadata["user_id"] = str(key.userids[0]) if key.userids else "unknown"
            metadata["name"] = key.userids[0].name if key.userids else "unknown"
            metadata["email"] = key.userids[0].email if key.userids else "unknown"
            metadata["created"] = key.created.strftime("%a, %d %b %Y %H:%M:%S %Z") if key.created else "unknown"
            metadata["expires"] = key.expires.strftime("%a, %d %b %Y %H:%M:%S %Z") if hasattr(key, 'expires') and key.expires else "never"
            metadata["fingerprint"] = key.fingerprint
            metadata["key_id"] = key.fingerprint[-16:]
            metadata["algorithm"] = key.key_algorithm.name
            metadata["can_sign"] = key.can_sign
            metadata["can_encrypt"] = key.can_encrypt
            metadata["can_certify"] = key.can_certify
            metadata["rawout"] = key

    except Exception as e:
        print(Fore.RED + f"error reading gpg key block: {e}")
    return metadata