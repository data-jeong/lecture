"""
텍스트 변환 모듈
텍스트를 다양한 방식으로 변환합니다.
"""

import re
import string

def to_uppercase(text):
    """모든 문자를 대문자로 변환합니다."""
    return text.upper()

def to_lowercase(text):
    """모든 문자를 소문자로 변환합니다."""
    return text.lower()

def to_title(text):
    """각 단어의 첫 글자를 대문자로 변환합니다."""
    return text.title()

def to_sentence_case(text):
    """문장의 첫 글자만 대문자로 변환합니다."""
    sentences = re.split(r'([.!?]+)', text)
    result = []
    
    for i, part in enumerate(sentences):
        if i % 2 == 0:  # 문장 부분
            part = part.strip()
            if part:
                part = part[0].upper() + part[1:].lower()
        result.append(part)
    
    return ''.join(result)

def remove_punctuation(text, keep_spaces=True):
    """구두점을 제거합니다."""
    if keep_spaces:
        # 공백은 유지하면서 구두점만 제거
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
    else:
        # 구두점을 공백으로 치환
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        return text.translate(translator)

def remove_extra_spaces(text):
    """연속된 공백을 하나의 공백으로 변환합니다."""
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return text.strip()

def align_text(text, width=50, align='left'):
    """텍스트를 정렬합니다."""
    lines = text.split('\n')
    aligned_lines = []
    
    for line in lines:
        line = line.strip()
        if align == 'left':
            aligned_lines.append(line.ljust(width))
        elif align == 'right':
            aligned_lines.append(line.rjust(width))
        elif align == 'center':
            aligned_lines.append(line.center(width))
        else:
            aligned_lines.append(line)
    
    return '\n'.join(aligned_lines)

def replace_words(text, replacements):
    """단어를 일괄 치환합니다."""
    for old_word, new_word in replacements.items():
        # 단어 경계를 사용하여 정확한 단어만 치환
        pattern = r'\b' + re.escape(old_word) + r'\b'
        text = re.sub(pattern, new_word, text, flags=re.IGNORECASE)
    
    return text

def reverse_text(text):
    """텍스트를 거꾸로 뒤집습니다."""
    return text[::-1]

def reverse_words(text):
    """단어 순서를 거꾸로 뒤집습니다."""
    words = text.split()
    return ' '.join(reversed(words))

def remove_numbers(text):
    """숫자를 제거합니다."""
    return re.sub(r'\d+', '', text)

def extract_numbers(text):
    """텍스트에서 숫자만 추출합니다."""
    numbers = re.findall(r'\d+', text)
    return ' '.join(numbers)

def camel_to_snake(text):
    """CamelCase를 snake_case로 변환합니다."""
    # 대문자 앞에 언더스코어 추가
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(text):
    """snake_case를 CamelCase로 변환합니다."""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def wrap_text(text, width=80):
    """텍스트를 지정된 너비로 줄바꿈합니다."""
    import textwrap
    return textwrap.fill(text, width=width)

def truncate_text(text, max_length=100, suffix='...'):
    """텍스트를 지정된 길이로 자릅니다."""
    if len(text) <= max_length:
        return text
    
    # 단어 경계에서 자르기
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # 80% 이상 위치에 공백이 있으면
        truncated = truncated[:last_space]
    
    return truncated + suffix

def normalize_whitespace(text):
    """모든 종류의 공백을 일반 공백으로 변환합니다."""
    # 탭, 줄바꿈, 기타 공백 문자를 일반 공백으로
    text = re.sub(r'[\t\r\f\v]', ' ', text)
    # 연속된 공백 제거
    text = re.sub(r' +', ' ', text)
    # 줄바꿈 정규화
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def remove_html_tags(text):
    """HTML 태그를 제거합니다."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def mask_sensitive_data(text):
    """민감한 정보를 마스킹합니다."""
    # 이메일 마스킹
    text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                  lambda m: m.group(1)[:3] + '***@' + m.group(2), text)
    
    # 전화번호 마스킹
    text = re.sub(r'(\d{3})-(\d{4})-(\d{4})',
                  r'\1-****-\3', text)
    
    # 주민번호 마스킹
    text = re.sub(r'(\d{6})-(\d{7})',
                  r'\1-*******', text)
    
    return text