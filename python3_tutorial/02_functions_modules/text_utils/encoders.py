"""
텍스트 인코딩/디코딩 모듈
다양한 인코딩 방식을 지원하는 유틸리티 함수들
"""

import base64
import hashlib
import html
import urllib.parse
from typing import Optional


def encode_base64(text: str) -> str:
    """텍스트를 Base64로 인코딩합니다."""
    try:
        encoded_bytes = base64.b64encode(text.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Error encoding to Base64: {e}"


def decode_base64(encoded_text: str) -> str:
    """Base64 인코딩된 텍스트를 디코딩합니다."""
    try:
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Error decoding from Base64: {e}"


def encode_url(text: str) -> str:
    """URL 인코딩을 수행합니다."""
    return urllib.parse.quote(text)


def decode_url(encoded_text: str) -> str:
    """URL 디코딩을 수행합니다."""
    return urllib.parse.unquote(encoded_text)


def encode_html(text: str) -> str:
    """HTML 엔티티 인코딩을 수행합니다."""
    return html.escape(text)


def decode_html(encoded_text: str) -> str:
    """HTML 엔티티 디코딩을 수행합니다."""
    return html.unescape(encoded_text)


def hash_md5(text: str) -> str:
    """MD5 해시를 생성합니다."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def hash_sha256(text: str) -> str:
    """SHA256 해시를 생성합니다."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def hash_sha512(text: str) -> str:
    """SHA512 해시를 생성합니다."""
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def rot13(text: str) -> str:
    """ROT13 인코딩/디코딩을 수행합니다."""
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)


def to_hex(text: str) -> str:
    """텍스트를 16진수로 변환합니다."""
    return text.encode('utf-8').hex()


def from_hex(hex_text: str) -> str:
    """16진수를 텍스트로 변환합니다."""
    try:
        return bytes.fromhex(hex_text).decode('utf-8')
    except Exception as e:
        return f"Error converting from hex: {e}"


def to_binary(text: str) -> str:
    """텍스트를 이진수로 변환합니다."""
    return ' '.join(format(ord(char), '08b') for char in text)


def from_binary(binary_text: str) -> str:
    """이진수를 텍스트로 변환합니다."""
    try:
        binary_values = binary_text.split()
        return ''.join(chr(int(b, 2)) for b in binary_values)
    except Exception as e:
        return f"Error converting from binary: {e}"


def caesar_cipher(text: str, shift: int = 3) -> str:
    """시저 암호 인코딩/디코딩을 수행합니다."""
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
        else:
            result.append(char)
    return ''.join(result)


def reverse_text(text: str) -> str:
    """텍스트를 역순으로 변환합니다."""
    return text[::-1]


def morse_encode(text: str) -> str:
    """텍스트를 모스 부호로 변환합니다."""
    morse_code = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', ' ': '/'
    }
    
    result = []
    for char in text.upper():
        if char in morse_code:
            result.append(morse_code[char])
        elif char == ' ':
            result.append('/')
    
    return ' '.join(result)


def morse_decode(morse_text: str) -> str:
    """모스 부호를 텍스트로 변환합니다."""
    morse_code = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
        '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
        '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
        '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
        '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9', '/': ' '
    }
    
    result = []
    for code in morse_text.split():
        if code in morse_code:
            result.append(morse_code[code])
    
    return ''.join(result)