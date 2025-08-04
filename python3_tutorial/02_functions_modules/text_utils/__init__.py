"""
텍스트 처리 유틸리티 패키지
다양한 텍스트 처리 기능을 제공합니다.
"""

from .statistics import (
    count_words,
    count_sentences,
    count_characters,
    average_word_length,
    word_frequency,
    get_statistics,
    reading_time,
    readability_score
)

from .transformers import (
    to_uppercase,
    to_lowercase,
    to_title,
    remove_punctuation,
    remove_extra_spaces,
    align_text,
    replace_words,
    mask_sensitive_data,
    wrap_text
)

from .searchers import (
    find_pattern,
    find_all_patterns,
    find_emails,
    find_phone_numbers,
    find_urls,
    highlight_pattern,
    find_dates
)

from .file_handlers import (
    read_text_file,
    write_text_file,
    process_multiple_files,
    merge_files,
    split_file,
    get_file_info,
    backup_file
)

# New modules
try:
    from .encoders import (
        encode_base64, decode_base64, encode_url, decode_url,
        encode_html, decode_html, hash_md5, hash_sha256, hash_sha512,
        rot13, caesar_cipher, morse_encode, morse_decode,
        to_hex, from_hex, to_binary, from_binary, reverse_text
    )
except ImportError:
    pass

try:
    from .analyzers import (
        analyze_sentiment, extract_keywords, language_detection,
        text_complexity, find_named_entities, text_similarity,
        extract_summary, detect_plagiarism
    )
except ImportError:
    pass

__version__ = '1.1.0'
__author__ = '김파이썬'

__all__ = [
    # statistics
    'count_words',
    'count_sentences',
    'count_characters',
    'average_word_length',
    'word_frequency',
    'get_statistics',
    'reading_time',
    'readability_score',
    
    # transformers
    'to_uppercase',
    'to_lowercase',
    'to_title',
    'remove_punctuation',
    'remove_extra_spaces',
    'align_text',
    'replace_words',
    'mask_sensitive_data',
    'wrap_text',
    
    # searchers
    'find_pattern',
    'find_all_patterns',
    'find_emails',
    'find_phone_numbers',
    'find_urls',
    'highlight_pattern',
    'find_dates',
    
    # file_handlers
    'read_text_file',
    'write_text_file',
    'process_multiple_files',
    'merge_files',
    'split_file',
    'get_file_info',
    'backup_file'
]