# 📦 02. 함수와 모듈 - 텍스트 처리 유틸리티

## 🎯 프로젝트 목표
Python의 함수와 모듈 개념을 학습하면서 실용적인 텍스트 처리 유틸리티를 만드는 프로젝트입니다. 모듈화된 코드 작성과 재사용 가능한 함수 설계를 통해 깔끔하고 효율적인 프로그램을 개발합니다.

## 📚 핵심 학습 주제
- 🔧 **함수 정의와 매개변수** (*args, **kwargs)
- ⚡ **람다 함수와 고차 함수**
- 🏗️ **모듈과 패키지 구조**
- 🔍 **정규표현식 (regex)**
- 📁 **파일 입출력**
- 🖥️ **명령줄 인자 처리** (argparse)
- ✨ **데코레이터**
- 📊 **텍스트 분석 알고리즘**

## 📁 프로젝트 구조
```
02_functions_modules/
├── 📄 README.md              # 종합 가이드
├── 📋 PROJECT_PLAN.md       # 프로젝트 계획서
├── 📚 step_by_step.md       # 단계별 학습 가이드
├── 🖥️ main.py               # CLI 메인 프로그램
├── 🎯 examples.py           # 실용적인 사용 예제
├── 🧪 tests.py              # 자동화된 테스트
├── 📋 requirements.txt      # 의존성 목록
├── 📁 backup/               # 자동 백업 폴더
├── 📄 sample.txt            # 테스트용 샘플 파일
└── 📦 text_utils/           # 텍스트 처리 패키지
    ├── 🔧 __init__.py       # 패키지 초기화 및 API
    ├── 📊 statistics.py     # 텍스트 통계 분석
    ├── 🔄 transformers.py   # 텍스트 변환 도구
    ├── 🔍 searchers.py      # 패턴 검색 엔진
    ├── 📁 file_handlers.py  # 파일 처리 유틸리티
    ├── 📝 analyzers.py      # 고급 텍스트 분석
    └── 🔐 encoders.py       # 인코딩/디코딩 도구
```

## 🚀 빠른 시작 가이드

### 1️⃣ 설치 및 설정
```bash
# 프로젝트 디렉토리로 이동
cd 02_functions_modules

# 의존성 설치 (필요한 경우)
pip install -r requirements.txt
```

### 2️⃣ 기본 실행 방법
```bash
# 🎮 대화형 모드 (추천)
python main.py -i

# 📊 파일 통계 분석
python main.py -f sample.txt -a stats

# 🔄 텍스트 변환 (대문자로)
python main.py -f sample.txt -a transform -t upper -o output.txt

# 🔍 패턴 검색 (이메일, 전화번호 등)
python main.py -f sample.txt -a search

# 🎯 사용 예제 실행
python examples.py
```

### 3️⃣ 테스트 실행
```bash
# 모든 테스트 실행
python tests.py

# 또는 pytest 사용
pytest tests.py -v
```

## ✨ 주요 기능

### 📊 1. 텍스트 통계 분석
- **기본 통계**: 단어 수, 문장 수, 문자 수, 단락 수
- **고급 분석**: 평균 단어/문장 길이, 어휘 다양성
- **빈도 분석**: 단어 빈도, N-gram 분석
- **가독성 평가**: Flesch 가독성 점수, 복잡도 측정
- **시간 예측**: 예상 읽기 시간, 음성 변환 시간

### 🔄 2. 텍스트 변환
- **케이스 변환**: 대문자, 소문자, 제목 케이스, 캐멀 케이스
- **정리 도구**: 공백 정리, 개행 정규화, 탭 변환
- **필터링**: 구두점 제거, 숫자 제거, 특수문자 처리
- **보안 도구**: 민감정보 마스킹, 개인정보 익명화
- **포맷팅**: 텍스트 정렬, 줄 바꿈, 들여쓰기

### 🔍 3. 스마트 패턴 검색
- **연락처 정보**: 이메일 주소, 전화번호, 팩스번호
- **웹 리소스**: URL, 도메인, IP 주소
- **날짜/시간**: 다양한 날짜 형식, 시간 표현
- **정규표현식**: 사용자 정의 패턴 검색
- **소셜 미디어**: 해시태그, 멘션, 이모지
- **코드 패턴**: 변수명, 함수명, 주석

### 📁 4. 파일 처리 시스템
- **입출력**: UTF-8/ASCII 인코딩, 대용량 파일 처리
- **일괄 처리**: 디렉토리 내 모든 파일 처리
- **파일 관리**: 자동 백업, 버전 관리, 중복 제거
- **변환**: 파일 포맷 변환, 인코딩 변환
- **분석**: 파일 비교, 차이점 검출

## 💡 핵심 코드 패턴 & 예제

### 📊 텍스트 통계 분석
```python
from text_utils import get_statistics, word_frequency, reading_time

# 기본 통계 분석
text = """
Python은 배우기 쉽고 강력한 프로그래밍 언어입니다.
데이터 분석, 웹 개발, 인공지능 등 다양한 분야에서 활용됩니다.
"""

stats = get_statistics(text)
print(f"📄 단어 수: {stats['단어 수']}")
print(f"📝 문장 수: {stats['문장 수']}")
print(f"⏱️ 예상 읽기 시간: {reading_time(text)}")

# 단어 빈도 분석
top_words = word_frequency(text, top_n=5)
for word, count in top_words:
    print(f"'{word}': {count}번")
```

### 🔄 텍스트 변환
```python
from text_utils import (
    to_uppercase, to_lowercase, remove_extra_spaces, 
    mask_sensitive_data, remove_punctuation
)

# 다양한 변환 예제
original = "  Hello, Python World!  연락처: user@example.com  "

print("🔤 대문자:", to_uppercase(original))
print("🔡 소문자:", to_lowercase(original))
print("🧹 공백 정리:", remove_extra_spaces(original))
print("🚫 구두점 제거:", remove_punctuation(original))
print("🔐 민감정보 마스킹:", mask_sensitive_data(original))
```

### 🔍 스마트 패턴 검색
```python
from text_utils import find_emails, find_phone_numbers, find_urls, find_dates

contact_text = """
연락처 정보:
이메일: john.doe@company.co.kr, support@example.com
전화: 010-1234-5678, +82-2-123-4567
웹사이트: https://www.python.org, http://github.com
날짜: 2024-01-15, 2024/12/31
"""

print("📧 이메일:", find_emails(contact_text))
print("📞 전화번호:", find_phone_numbers(contact_text))
print("🌐 URL:", find_urls(contact_text))
print("📅 날짜:", find_dates(contact_text))
```

### 📁 파일 처리
```python
from text_utils import read_text_file, write_text_file, process_multiple_files

# 단일 파일 처리
content = read_text_file("sample.txt")
if content:
    # 텍스트 처리
    processed = content.upper().strip()
    write_text_file("output.txt", processed)

# 여러 파일 일괄 처리
results = process_multiple_files(
    directory="./data/",
    pattern="*.txt",
    operation="statistics"
)
```

## 🎓 핵심 학습 패턴

### 🔧 1. 함수의 다양한 형태
```python
# 기본 함수 정의
def greet(name):
    """기본적인 인사 함수"""
    return f"Hello, {name}!"

# 기본값 매개변수 활용
def greet_with_default(name="World", style="formal"):
    """기본값이 있는 매개변수 사용"""
    styles = {
        "formal": f"안녕하세요, {name}님!",
        "casual": f"안녕, {name}!",
        "english": f"Hello, {name}!"
    }
    return styles.get(style, styles["formal"])

# 가변 인자 (*args) 사용 
def calculate_stats(*values):
    """여러 값을 받아 통계 계산"""
    if not values:
        return None
    return {
        'count': len(values),
        'sum': sum(values),
        'average': sum(values) / len(values)
    }

# 키워드 인자 (**kwargs) 활용
def create_text_processor(**options):
    """설정 옵션을 받아 텍스트 처리기 생성"""
    defaults = {
        'case_sensitive': True,
        'remove_punctuation': False,
        'encoding': 'utf-8'
    }
    defaults.update(options)
    return defaults

# 람다 함수와 고차 함수
words = ["python", "java", "javascript", "go"]
sorted_by_length = sorted(words, key=lambda x: len(x))
filtered_words = list(filter(lambda x: len(x) > 4, words))
```

### 🏗️ 2. 모듈과 패키지 구조
```python
# text_utils/__init__.py - 패키지 초기화
"""
텍스트 처리 유틸리티 패키지
다양한 텍스트 분석 및 변환 도구 제공
"""

# 공개 API 정의
__all__ = [
    'get_statistics', 'word_frequency', 'reading_time',
    'to_uppercase', 'to_lowercase', 'remove_punctuation',
    'find_emails', 'find_phone_numbers', 'find_urls',
    'read_text_file', 'write_text_file'
]

# 하위 모듈에서 함수 import
from .statistics import get_statistics, word_frequency, reading_time
from .transformers import to_uppercase, to_lowercase, remove_punctuation
from .searchers import find_emails, find_phone_numbers, find_urls
from .file_handlers import read_text_file, write_text_file

# 버전 정보
__version__ = "1.0.0"
__author__ = "Python Tutorial"
```

### 🔍 3. 정규표현식 마스터
```python
import re

# 이메일 패턴 (RFC 5322 표준 기반)
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# 한국 전화번호 패턴
PHONE_PATTERNS = [
    r'010-\d{4}-\d{4}',          # 010-1234-5678
    r'\+82-\d{1,2}-\d{3,4}-\d{4}', # +82-2-123-4567
    r'\d{2,3}-\d{3,4}-\d{4}'     # 02-123-4567
]

# URL 패턴
URL_PATTERN = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'

# 날짜 패턴 (다양한 형식)
DATE_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',        # 2024-01-15
    r'\d{4}/\d{2}/\d{2}',        # 2024/01/15
    r'\d{2}\.\d{2}\.\d{4}'       # 15.01.2024
]

def find_pattern_with_context(text, pattern, context_size=20):
    """패턴을 찾고 주변 문맥도 함께 반환"""
    matches = []
    for match in re.finditer(pattern, text):
        start = max(0, match.start() - context_size)
        end = min(len(text), match.end() + context_size)
        context = text[start:end]
        matches.append({
            'match': match.group(),
            'context': context,
            'position': (match.start(), match.end())
        })
    return matches
```

### 📁 4. 고급 파일 처리
```python
from pathlib import Path
import chardet
import shutil
from datetime import datetime

def smart_file_reader(file_path):
    """인코딩을 자동 감지하여 파일 읽기"""
    path = Path(file_path)
    
    # 파일 존재 확인
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    
    # 인코딩 감지
    with open(path, 'rb') as f:
        raw_data = f.read()
        encoding = chardet.detect(raw_data)['encoding']
    
    # 텍스트 읽기
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        # 대체 인코딩 시도
        for fallback_encoding in ['utf-8', 'euc-kr', 'cp949']:
            try:
                return path.read_text(encoding=fallback_encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("파일 인코딩을 감지할 수 없습니다")

def backup_file(file_path):
    """파일 백업 생성"""
    path = Path(file_path)
    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.parent / "backup" / f"{timestamp}_{path.name}"
        backup_path.parent.mkdir(exist_ok=True)
        shutil.copy2(path, backup_path)
        return backup_path
    return None
```

## ✅ 학습 체크리스트

### 🔧 함수 및 모듈 설계
- [ ] 기본 함수 정의와 반환값 처리
- [ ] 매개변수 종류별 활용 (*args, **kwargs, 기본값)
- [ ] 람다 함수와 함수형 프로그래밍 기법
- [ ] 데코레이터를 활용한 함수 확장
- [ ] 모듈과 패키지 구조 설계
- [ ] __init__.py를 통한 패키지 API 정의

### 🔍 텍스트 처리 기술
- [ ] 정규표현식 패턴 작성과 매칭
- [ ] 다양한 텍스트 인코딩 처리
- [ ] 파일 입출력과 예외 처리
- [ ] 텍스트 통계 알고리즘 구현
- [ ] 문자열 변환과 정제 기법

### 🖥️ CLI 도구 개발
- [ ] argparse를 활용한 명령줄 인터페이스
- [ ] 대화형 모드와 배치 모드 구현
- [ ] 에러 처리와 사용자 피드백
- [ ] 도움말과 사용법 문서화

## 🔧 문제 해결 가이드

### ❌ 자주 발생하는 오류
```python
# 1. 인코딩 오류
# UnicodeDecodeError: 'utf-8' codec can't decode byte
# 해결: chardet 라이브러리로 인코딩 자동 감지

# 2. 파일 경로 오류  
# FileNotFoundError: No such file or directory
# 해결: pathlib.Path로 경로 검증

# 3. 정규표현식 오류
# re.error: bad character range
# 해결: 특수문자 이스케이프 처리

# 4. 메모리 오류 (대용량 파일)
# MemoryError: Unable to allocate array
# 해결: 스트리밍 방식으로 파일 처리
```

### 💡 성능 최적화 팁
- **제너레이터 사용**: 대용량 텍스트 처리 시 메모리 절약
- **컴파일된 정규표현식**: re.compile() 활용으로 속도 향상  
- **배치 처리**: 여러 파일을 한 번에 처리하여 I/O 최적화
- **캐싱**: 반복적인 연산 결과를 저장하여 재사용

## 🚀 확장 아이디어

### 🎯 중급 확장
1. **GUI 인터페이스**: tkinter/PyQt로 데스크톱 앱 개발
2. **웹 대시보드**: Flask/FastAPI로 웹 인터페이스 구축
3. **다국어 지원**: 다양한 언어의 텍스트 처리
4. **플러그인 시스템**: 사용자 정의 처리 모듈 추가

### 🔥 고급 확장  
1. **자연어 처리**: NLTK/spaCy 통합으로 고급 분석
2. **머신러닝**: 텍스트 분류 및 감정 분석
3. **클라우드 연동**: AWS/Google Cloud API 활용
4. **실시간 처리**: 웹소켓을 통한 실시간 텍스트 분석

## 📚 참고 자료
- [Python 정규표현식 가이드](https://docs.python.org/ko/3/library/re.html)
- [pathlib 모듈 문서](https://docs.python.org/ko/3/library/pathlib.html)
- [argparse 튜토리얼](https://docs.python.org/ko/3/howto/argparse.html)
- [텍스트 인코딩 이해하기](https://docs.python.org/ko/3/howto/unicode.html)

## ➡️ 다음 프로젝트
**[03. 객체지향 설계 - 도서관 관리 시스템](../03_oop_design/README.md)**  
객체지향 프로그래밍의 핵심 개념을 배우면서 실제 도서관 관리 시스템을 설계하고 구현합니다.