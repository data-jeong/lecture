"""
텍스트 처리 유틸리티 사용 예제
다양한 텍스트 처리 기능의 활용 예시
"""

from text_utils import *

def example_statistics():
    """텍스트 통계 예제"""
    print("=== 텍스트 통계 예제 ===\n")
    
    text = """
    Python은 1991년 귀도 반 로섬(Guido van Rossum)이 발표한 프로그래밍 언어입니다.
    파이썬은 간결하고 읽기 쉬운 문법을 가지고 있어 초보자부터 전문가까지 널리 사용됩니다.
    웹 개발, 데이터 분석, 인공지능, 자동화 등 다양한 분야에서 활용되고 있습니다.
    
    연락처: python@example.com, 전화: 010-1234-5678
    웹사이트: https://www.python.org
    """
    
    # 기본 통계
    stats = get_statistics(text)
    print("텍스트 통계:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 단어 빈도
    print("\n가장 많이 사용된 단어:")
    top_words = word_frequency(text, top_n=5)
    for word, count in top_words:
        print(f"  {word}: {count}회")
    
    # 읽기 시간과 가독성
    print(f"\n예상 읽기 시간: {reading_time(text)}")
    print(f"가독성 점수: {readability_score(text)}")

def example_transformers():
    """텍스트 변환 예제"""
    print("\n\n=== 텍스트 변환 예제 ===\n")
    
    text = "  Hello,   Python   World!  "
    
    print(f"원본: '{text}'")
    print(f"대문자: '{to_uppercase(text)}'")
    print(f"소문자: '{to_lowercase(text)}'")
    print(f"제목: '{to_title(text)}'")
    print(f"공백 정리: '{remove_extra_spaces(text)}'")
    
    # 민감정보 마스킹
    sensitive_text = """
    이메일: john.doe@example.com
    전화번호: 010-1234-5678
    주민번호: 990101-1234567
    """
    
    print(f"\n민감정보 마스킹 전:{sensitive_text}")
    print(f"민감정보 마스킹 후:\n{mask_sensitive_data(sensitive_text)}")
    
    # 텍스트 정렬
    text = "Python Programming"
    print(f"\n텍스트 정렬 (폭 30):")
    print(f"왼쪽: '{align_text(text, 30, 'left')}'")
    print(f"가운데: '{align_text(text, 30, 'center')}'")
    print(f"오른쪽: '{align_text(text, 30, 'right')}'")
    
    # 단어 치환
    text = "I love Java. Java is great."
    replacements = {"Java": "Python"}
    print(f"\n단어 치환:")
    print(f"원본: {text}")
    print(f"치환 후: {replace_words(text, replacements)}")

def example_searchers():
    """패턴 검색 예제"""
    print("\n\n=== 패턴 검색 예제 ===\n")
    
    text = """
    연락처 정보:
    - 이메일: admin@company.com, support@company.co.kr
    - 전화: 02-1234-5678, 010-9876-5432, (031) 123-4567
    - 웹사이트: https://www.company.com, http://blog.company.com
    - 날짜: 2024-01-15, 2024년 3월 20일, 2024.05.30
    - 시간: 09:30 AM, 14:45, 18시 30분
    
    #파이썬 #프로그래밍 @python_official
    """
    
    # 이메일 찾기
    emails = find_emails(text)
    print(f"이메일 주소: {emails}")
    
    # 전화번호 찾기
    phones = find_phone_numbers(text)
    print(f"전화번호: {phones}")
    
    # URL 찾기
    urls = find_urls(text)
    print(f"URL: {urls}")
    
    # 날짜 찾기
    dates = find_dates(text)
    print(f"날짜: {dates}")
    
    # 시간 찾기 (find_times 함수 구현 필요)
    # times = find_times(text)
    # print(f"시간: {times}")
    
    # 해시태그와 멘션 (함수 구현 필요)
    # hashtags = find_hashtags(text)
    # mentions = find_mentions(text)
    # print(f"해시태그: {hashtags}")
    # print(f"멘션: {mentions}")
    
    # 패턴 강조
    pattern = r'\d{2,4}[-년./]\d{1,2}[-월./]\d{1,2}'
    highlighted = highlight_pattern(text, pattern, '**', '**')
    print(f"\n날짜 패턴 강조:\n{highlighted}")

def example_file_operations():
    """파일 처리 예제"""
    print("\n\n=== 파일 처리 예제 ===\n")
    
    # 샘플 파일 생성
    sample_content = """Python 텍스트 처리 예제
이것은 파일 처리를 테스트하기 위한 샘플 텍스트입니다.
여러 줄의 내용이 포함되어 있습니다.
    
연락처: test@example.com
날짜: 2024-01-15"""
    
    # 파일 쓰기
    if write_text_file('sample.txt', sample_content):
        print("sample.txt 파일을 생성했습니다.")
    
    # 파일 읽기
    content = read_text_file('sample.txt')
    if content:
        print(f"\n파일 내용 (처음 50자):\n{content[:50]}...")
    
    # 파일 정보
    info = get_file_info('sample.txt')
    print(f"\n파일 정보:")
    print(f"  이름: {info['name']}")
    print(f"  크기: {info['size_human']}")
    print(f"  확장자: {info['extension']}")
    
    # 파일 백업
    backup_path = backup_file('sample.txt')
    if backup_path:
        print(f"\n백업 생성: {backup_path}")
    
    # 여러 파일 처리 예제
    def uppercase_processor(text):
        return to_uppercase(text)
    
    # 파일이 있다면 처리
    import glob
    txt_files = glob.glob('*.txt')
    if txt_files:
        print(f"\n현재 디렉토리의 .txt 파일: {txt_files[:3]}...")  # 처음 3개만 표시

def example_advanced_usage():
    """고급 사용 예제"""
    print("\n\n=== 고급 사용 예제 ===\n")
    
    # 람다 함수와 함께 사용
    texts = [
        "Python programming",
        "java development",
        "JAVASCRIPT coding"
    ]
    
    # 모든 텍스트를 제목 형식으로
    titled_texts = list(map(to_title, texts))
    print(f"제목 형식 변환: {titled_texts}")
    
    # 필터링
    long_texts = list(filter(lambda x: len(x) > 15, texts))
    print(f"15자 이상 텍스트: {long_texts}")
    
    # 데코레이터 예제
    def log_function_call(func):
        def wrapper(*args, **kwargs):
            print(f"함수 호출: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"결과 타입: {type(result)}")
            return result
        return wrapper
    
    @log_function_call
    def process_text(text):
        return remove_extra_spaces(to_lowercase(text))
    
    result = process_text("  HELLO   WORLD  ")
    print(f"처리 결과: '{result}'")

def example_real_world():
    """실제 활용 예제"""
    print("\n\n=== 실제 활용 예제 ===\n")
    
    # 1. 로그 파일 분석
    log_text = """
    [2024-01-15 09:30:15] INFO: 서버 시작
    [2024-01-15 09:30:45] ERROR: 데이터베이스 연결 실패 (user@example.com)
    [2024-01-15 09:31:20] INFO: 재시도 중...
    [2024-01-15 09:31:25] SUCCESS: 연결 성공
    """
    
    # 에러 라인 찾기 (find_sentences_with_word 함수 구현 필요)
    # error_lines = find_sentences_with_word(log_text, "ERROR")
    # print("에러 로그:")
    # for line in error_lines:
    #     print(f"  {line}")
    
    # 2. 이력서 텍스트에서 연락처 추출
    resume_text = """
    이름: 김파이썬
    이메일: kim.python@example.com
    전화: 010-1234-5678
    
    경력:
    - Python 개발자 (2020-2023)
    - 웹사이트: https://github.com/kimpython
    """
    
    print("\n이력서에서 추출한 정보:")
    emails = find_emails(resume_text)
    phones = find_phone_numbers(resume_text)
    urls = find_urls(resume_text)
    
    print(f"  이메일: {emails}")
    print(f"  전화번호: {phones}")
    print(f"  웹사이트: {urls}")
    
    # 3. 텍스트 요약
    long_text = """
    Python은 귀도 반 로섬이 1991년에 발표한 고급 프로그래밍 언어입니다.
    파이썬은 플랫폼에 독립적이며 인터프리터식, 객체지향적, 동적 타이핑 언어입니다.
    파이썬은 비영리의 파이썬 소프트웨어 재단이 관리하는 개방형, 공동체 기반 개발 모델을 가지고 있습니다.
    """
    
    # truncate_text 함수 구현 필요
    # truncated = truncate_text(long_text, 100)
    # print(f"\n텍스트 요약:\n{truncated}")

def run_all_examples():
    """모든 예제 실행"""
    print("텍스트 처리 유틸리티 예제 모음\n")
    print("=" * 60)
    
    example_statistics()
    example_transformers()
    example_searchers()
    example_file_operations()
    example_advanced_usage()
    example_real_world()
    
    print("\n" + "=" * 60)
    print("모든 예제가 완료되었습니다!")
    print("더 자세한 사용법은 main.py -h를 참고하세요.")

if __name__ == "__main__":
    run_all_examples()