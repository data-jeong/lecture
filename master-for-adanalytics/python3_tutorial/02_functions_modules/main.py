"""
텍스트 처리 유틸리티 메인 프로그램
다양한 텍스트 처리 기능을 제공하는 CLI 도구
"""

import argparse
import sys
from pathlib import Path

# 텍스트 유틸리티 모듈 import
from text_utils import (
    # 통계
    get_statistics, word_frequency, reading_time, readability_score,
    # 변환
    to_uppercase, to_lowercase, to_title, remove_punctuation,
    remove_extra_spaces, mask_sensitive_data, wrap_text,
    # 검색
    find_emails, find_phone_numbers, find_urls, find_dates,
    find_pattern, highlight_pattern,
    # 파일 처리
    read_text_file, write_text_file, process_multiple_files
)

def display_statistics(text):
    """텍스트 통계를 표시합니다."""
    stats = get_statistics(text)
    
    print("\n=== 텍스트 통계 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\n예상 읽기 시간: {reading_time(text)}")
    print(f"가독성 점수: {readability_score(text)}")
    
    # 단어 빈도
    print("\n=== 가장 많이 사용된 단어 TOP 10 ===")
    top_words = word_frequency(text, top_n=10)
    for i, (word, count) in enumerate(top_words, 1):
        print(f"{i}. {word}: {count}회")

def transform_text(text, transform_type):
    """텍스트를 변환합니다."""
    transformations = {
        'upper': to_uppercase,
        'lower': to_lowercase,
        'title': to_title,
        'no-punct': remove_punctuation,
        'clean': remove_extra_spaces,
        'mask': mask_sensitive_data,
    }
    
    if transform_type in transformations:
        return transformations[transform_type](text)
    else:
        print(f"알 수 없는 변환 유형: {transform_type}")
        return text

def search_patterns(text):
    """텍스트에서 다양한 패턴을 검색합니다."""
    print("\n=== 패턴 검색 결과 ===")
    
    # 이메일
    emails = find_emails(text)
    if emails:
        print(f"\n이메일 주소 ({len(emails)}개):")
        for email in emails:
            print(f"  - {email}")
    
    # 전화번호
    phones = find_phone_numbers(text)
    if phones:
        print(f"\n전화번호 ({len(phones)}개):")
        for phone in phones:
            print(f"  - {phone}")
    
    # URL
    urls = find_urls(text)
    if urls:
        print(f"\nURL ({len(urls)}개):")
        for url in urls:
            print(f"  - {url}")
    
    # 날짜
    dates = find_dates(text)
    if dates:
        print(f"\n날짜 ({len(dates)}개):")
        for date in dates:
            print(f"  - {date}")

def interactive_mode():
    """대화형 모드로 실행합니다."""
    print("텍스트 처리 유틸리티 - 대화형 모드")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.\n")
    
    while True:
        print("\n메뉴:")
        print("1. 텍스트 통계")
        print("2. 텍스트 변환")
        print("3. 패턴 검색")
        print("4. 파일 처리")
        print("0. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice in ['0', 'quit', 'exit']:
            print("프로그램을 종료합니다.")
            break
        
        if choice == '1':
            text = input("\n텍스트를 입력하세요 (여러 줄은 Enter 두 번): \n")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            text = '\n'.join(lines)
            
            display_statistics(text)
        
        elif choice == '2':
            text = input("\n변환할 텍스트를 입력하세요: ")
            print("\n변환 유형:")
            print("1. 대문자 (upper)")
            print("2. 소문자 (lower)")
            print("3. 제목 형식 (title)")
            print("4. 구두점 제거 (no-punct)")
            print("5. 공백 정리 (clean)")
            print("6. 민감정보 마스킹 (mask)")
            
            transform_choice = input("\n선택: ").strip()
            transform_map = {
                '1': 'upper', '2': 'lower', '3': 'title',
                '4': 'no-punct', '5': 'clean', '6': 'mask'
            }
            
            if transform_choice in transform_map:
                result = transform_text(text, transform_map[transform_choice])
                print(f"\n변환 결과:\n{result}")
        
        elif choice == '3':
            text = input("\n검색할 텍스트를 입력하세요: ")
            search_patterns(text)
        
        elif choice == '4':
            file_path = input("\n파일 경로를 입력하세요: ").strip()
            if Path(file_path).exists():
                text = read_text_file(file_path)
                if text:
                    print(f"\n파일을 성공적으로 읽었습니다. (크기: {len(text)} 문자)")
                    sub_choice = input("\n1. 통계 보기\n2. 변환하기\n3. 패턴 검색\n선택: ")
                    
                    if sub_choice == '1':
                        display_statistics(text)
                    elif sub_choice == '2':
                        # 변환 로직
                        pass
                    elif sub_choice == '3':
                        search_patterns(text)
            else:
                print("파일을 찾을 수 없습니다.")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='텍스트 처리 유틸리티',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python main.py -f sample.txt -a stats
  python main.py -f sample.txt -a transform -t upper -o output.txt
  python main.py -f sample.txt -a search
  python main.py -i  # 대화형 모드
        """
    )
    
    parser.add_argument('-f', '--file', help='입력 파일 경로')
    parser.add_argument('-o', '--output', help='출력 파일 경로')
    parser.add_argument('-a', '--action', 
                        choices=['stats', 'transform', 'search'],
                        help='수행할 작업')
    parser.add_argument('-t', '--transform',
                        choices=['upper', 'lower', 'title', 'no-punct', 'clean', 'mask'],
                        help='변환 유형')
    parser.add_argument('-p', '--pattern', help='검색할 패턴')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='대화형 모드로 실행')
    
    args = parser.parse_args()
    
    # 대화형 모드
    if args.interactive:
        interactive_mode()
        return
    
    # 파일 기반 처리
    if args.file:
        text = read_text_file(args.file)
        if not text:
            print(f"파일을 읽을 수 없습니다: {args.file}")
            sys.exit(1)
        
        # 통계
        if args.action == 'stats':
            display_statistics(text)
        
        # 변환
        elif args.action == 'transform':
            if not args.transform:
                print("변환 유형을 지정해주세요 (-t)")
                sys.exit(1)
            
            result = transform_text(text, args.transform)
            
            if args.output:
                if write_text_file(args.output, result):
                    print(f"결과를 {args.output}에 저장했습니다.")
            else:
                print(result)
        
        # 검색
        elif args.action == 'search':
            if args.pattern:
                matches = find_pattern(text, args.pattern)
                if matches:
                    print(f"패턴 '{args.pattern}' 발견:")
                    print(matches)
                else:
                    print(f"패턴 '{args.pattern}'을 찾을 수 없습니다.")
            else:
                search_patterns(text)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()