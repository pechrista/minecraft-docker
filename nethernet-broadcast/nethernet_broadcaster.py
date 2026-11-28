import hashlib
import hmac
import ipaddress
import os
import random
import re
import socket
import struct
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

LISTEN_PORT = 7551
KEY = hashlib.sha256(b"\xde\xad\xbe\xef").digest()

# NetherNet discovery packet IDs
PKT_REQUEST = 0x00
PKT_RESPONSE = 0x01
PKT_MESSAGE = 0x02


def detect_broadcast_ip() -> str:
    """
    Resolves the local subnet broadcast address automatically.
    Checks BROADCAST_IP first, then Linux `ip` output, then macOS `ifconfig en0`,
    and falls back to 255.255.255.255.
    """
    env_override = os.getenv("BROADCAST_IP", "").strip()
    if env_override:
        return env_override

    # Linux / Docker (host network)
    try:
        out = subprocess.check_output(
            ["ip", "-o", "-f", "inet", "addr", "show"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            parts = line.split()
            if "inet" in parts:
                cidr = parts[parts.index("inet") + 1]
                iface = ipaddress.IPv4Interface(cidr)
                if not iface.ip.is_loopback and not iface.ip.is_link_local:
                    return str(iface.network.broadcast_address)
    except Exception:
        pass

    # macOS fallback on en0
    try:
        out = subprocess.check_output(
            ["ifconfig", "en0"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        match = re.search(
            r"inet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+0x([0-9a-fA-F]{8})",
            out,
        )
        if match:
            ip_str, mask_hex = match.groups()
            mask_str = socket.inet_ntoa(int(mask_hex, 16).to_bytes(4, "big"))
            iface = ipaddress.IPv4Interface(f"{ip_str}/{mask_str}")
            return str(iface.network.broadcast_address)
    except Exception:
        pass

    return "255.255.255.255"


def encrypt_packet(plaintext: bytes) -> bytes:
    """Encrypts plaintext with AES-ECB and prepends a 32-byte HMAC-SHA256."""
    pad_len = (16 - (len(plaintext) % 16)) % 16
    padded = plaintext + (b"\x00" * pad_len)
    cipher = Cipher(algorithms.AES(KEY), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    mac = hmac.new(KEY, ciphertext, hashlib.sha256).digest()
    return mac + ciphertext


def decrypt_packet(datagram: bytes) -> bytes | None:
    """Verifies the 32-byte HMAC-SHA256 and decrypts AES-ECB datagram."""
    if len(datagram) < 32:
        return None
    mac, ciphertext = datagram[:32], datagram[32:]
    expected_mac = hmac.new(KEY, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected_mac) or len(ciphertext) % 16 != 0:
        return None
    cipher = Cipher(algorithms.AES(KEY), modes.ECB())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def encode_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def build_server_data(
    server_name: str,
    level_name: str,
    game_type