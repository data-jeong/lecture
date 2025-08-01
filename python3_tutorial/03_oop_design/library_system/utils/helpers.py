"""
헬퍼 함수들
"""

from datetime import datetime

def format_currency(amount):
    """통화 형식으로 변환"""
    return f"₩{amount:,}"

def format_date(date, format_string="%Y년 %m월 %d일"):
    """날짜 형식 변환"""
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    return date.strftime(format_string)

def generate_report(library, report_type="summary"):
    """리포트 생성"""
    if report_type == "summary":
        return _generate_summary_report(library)
    elif report_type == "overdue":
        return _generate_overdue_report(library)
    elif report_type == "popular":
        return _generate_popular_books_report(library)
    else:
        return "알 수 없는 리포트 타입입니다."

def _generate_summary_report(library):
    """요약 리포트"""
    stats = library.get_statistics()
    
    report = f"""
{'='*50}
{library.name} 운영 현황 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

[도서 현황]
- 총 보유 도서: {stats['books']['total']:,}권
- 대출 가능: {stats['books']['available']:,}권
- 대출 중: {stats['books']['borrowed']:,}권

[도서 유형별 현황]
"""
    
    for book_type, count in stats['books']['types'].items():
        report += f"- {book_type}: {count:,}권\n"
    
    report += f"""
[회원 현황]
- 총 회원: {stats['members']['total']:,}명
- 활성 회원: {stats['members']['active']:,}명

[회원 유형별 현황]
"""
    
    for member_type, count in stats['members']['types'].items():
        report += f"- {member_type}: {count:,}명\n"
    
    report += f"""
[거래 현황]
- 총 거래: {stats['transactions']['total']:,}건
- 대출: {stats['transactions']['borrows']:,}건
- 반납: {stats['transactions']['returns']:,}건
- 연체: {stats['transactions']['overdue']:,}건
- 완료율: {stats['transactions']['completion_rate']}
{'='*50}
"""
    
    return report

def _generate_overdue_report(library):
    """연체 리포트"""
    overdue_list = library.get_overdue_books()
    
    report = f"""
{'='*50}
연체 도서 현황 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

총 연체 건수: {len(overdue_list)}건

"""
    
    if not overdue_list:
        report += "현재 연체된 도서가 없습니다.\n"
    else:
        report += f"{'No.':<5} {'도서명':<20} {'대출자':<10} {'연체일':<8} {'연체료':<10}\n"
        report += "-" * 60 + "\n"
        
        for i, item in enumerate(overdue_list, 1):
            book = item['book']
            member = item['member']
            
            report += (f"{i:<5} "
                      f"{book.title[:18]:<20} "
                      f"{member.name[:8]:<10} "
                      f"{item['overdue_days']:<8} "
                      f"{format_currency(item['fine']):<10}\n")
        
        total_fine = sum(item['fine'] for item in overdue_list)
        report += "-" * 60 + "\n"
        report += f"{'총 연체료:':<43} {format_currency(total_fine)}\n"
    
    report += "=" * 50 + "\n"
    
    return report

def _generate_popular_books_report(library):
    """인기 도서 리포트"""
    # 대출 횟수 계산
    borrow_count = {}
    
    for transaction in library.transaction_history.transactions:
        if transaction.transaction_type.value == "대출":
            book_id = transaction.book_id
            borrow_count[book_id] = borrow_count.get(book_id, 0) + 1
    
    # 정렬
    popular_books = sorted(borrow_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    report = f"""
{'='*50}
인기 도서 TOP 10
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

"""
    
    if not popular_books:
        report += "아직 대출 기록이 없습니다.\n"
    else:
        report += f"{'순위':<5} {'도서명':<25} {'저자':<15} {'대출횟수':<10}\n"
        report += "-" * 60 + "\n"
        
        for rank, (book_id, count) in enumerate(popular_books, 1):
            if book_id in library.books:
                book = library.books[book_id]
                report += (f"{rank:<5} "
                          f"{book.title[:23]:<25} "
                          f"{book.author[:13]:<15} "
                          f"{count}회\n")
    
    report += "=" * 50 + "\n"
    
    return report

def calculate_statistics(data_list, key_func):
    """통계 계산"""
    if not data_list:
        return {
            'count': 0,
            'min': 0,
            'max': 0,
            'avg': 0
        }
    
    values = [key_func(item) for item in data_list]
    
    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values)
    }

def paginate(items, page=1, per_page=10):
    """페이지네이션"""
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }