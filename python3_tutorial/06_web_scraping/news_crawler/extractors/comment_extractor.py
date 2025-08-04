"""
댓글 추출기
뉴스 기사의 댓글 추출
"""

import re
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import json

from ..utils.parser import HTMLParser


class CommentExtractor:
    """댓글 추출기"""
    
    def __init__(self):
        self.parser = HTMLParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 댓글 영역 선택자
        self.comment_selectors = [
            '.comments', '.comment-list', '#comments',
            '[class*="comment"]', '[id*="comment"]',
            '.disqus-thread', '#disqus_thread'
        ]
        
        # 개별 댓글 선택자
        self.single_comment_selectors = [
            '.comment', '.comment-item', 'article.comment',
            '[class*="comment-box"]', 'li.comment'
        ]
    
    def extract(self, html: str, url: str) -> List[Dict[str, Any]]:
        """HTML에서 댓글 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        comments = []
        
        # 댓글 영역 찾기
        comment_area = self._find_comment_area(soup)
        if not comment_area:
            self.logger.debug("No comment area found")
            return comments
        
        # 개별 댓글 추출
        for comment_elem in self._find_comments(comment_area):
            comment_data = self._extract_single_comment(comment_elem)
            if comment_data:
                comments.append(comment_data)
        
        self.logger.info(f"Extracted {len(comments)} comments")
        return comments
    
    def _find_comment_area(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """댓글 영역 찾기"""
        for selector in self.comment_selectors:
            area = soup.select_one(selector)
            if area:
                return area
        
        # 텍스트로 찾기
        for element in soup.find_all(['div', 'section']):
            if element.get('class'):
                class_str = ' '.join(element['class'])
                if 'comment' in class_str.lower():
                    return element
        
        return None
    
    def _find_comments(self, comment_area: BeautifulSoup) -> List[BeautifulSoup]:
        """개별 댓글 요소 찾기"""
        comments = []
        
        for selector in self.single_comment_selectors:
            found = comment_area.select(selector)
            if found:
                comments.extend(found)
                break
        
        # 선택자로 못 찾은 경우
        if not comments:
            # 구조 분석으로 찾기
            potential_comments = comment_area.find_all(['div', 'li', 'article'])
            for elem in potential_comments:
                # 댓글로 보이는 요소 확인
                if self._is_comment_element(elem):
                    comments.append(elem)
        
        return comments
    
    def _is_comment_element(self, element: BeautifulSoup) -> bool:
        """댓글 요소인지 확인"""
        # 클래스나 ID에 comment 포함
        if element.get('class'):
            if any('comment' in c for c in element['class']):
                return True
        
        if element.get('id') and 'comment' in element['id']:
            return True
        
        # 댓글 특징 확인 (작성자, 날짜, 내용)
        has_author = bool(element.find(['span', 'div'], class_=re.compile('author|user|name')))
        has_date = bool(element.find(['time', 'span'], class_=re.compile('date|time')))
        has_content = len(element.text.strip()) > 10
        
        return has_author and has_date and has_content
    
    def _extract_single_comment(self, comment_elem: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """단일 댓글 데이터 추출"""
        try:
            comment_data = {
                'id': self._extract_comment_id(comment_elem),
                'author': self._extract_author(comment_elem),
                'content': self._extract_content(comment_elem),
                'date': self._extract_date(comment_elem),
                'likes': self._extract_likes(comment_elem),
                'replies': self._extract_replies(comment_elem),
                'is_reply': self._is_reply(comment_elem),
                'parent_id': self._extract_parent_id(comment_elem)
            }
            
            # 최소 필수 데이터 확인
            if comment_data['content']:
                return comment_data
            
        except Exception as e:
            self.logger.debug(f"Error extracting comment: {e}")
        
        return None
    
    def _extract_comment_id(self, comment_elem: BeautifulSoup) -> Optional[str]:
        """댓글 ID 추출"""
        # ID 속성
        if comment_elem.get('id'):
            return comment_elem['id']
        
        # data-comment-id 등
        for attr in ['data-comment-id', 'data-id', 'data-cid']:
            if comment_elem.get(attr):
                return comment_elem[attr]
        
        return None
    
    def _extract_author(self, comment_elem: BeautifulSoup) -> Optional[str]:
        """작성자 추출"""
        author_selectors = [
            '.author', '.username', '.user-name',
            '.comment-author', '[class*="author"]',
            'span.name', 'a.name'
        ]
        
        for selector in author_selectors:
            author_elem = comment_elem.select_one(selector)
            if author_elem:
                return self.parser._clean_text(author_elem.text)
        
        return None
    
    def _extract_content(self, comment_elem: BeautifulSoup) -> Optional[str]:
        """댓글 내용 추출"""
        content_selectors = [
            '.comment-content', '.comment-text', '.content',
            '.message', '.text', '[class*="content"]',
            'p', 'div.body'
        ]
        
        for selector in content_selectors:
            content_elem = comment_elem.select_one(selector)
            if content_elem:
                # 대댓글, 액션 버튼 등 제거
                for remove in content_elem.select('.reply, .actions, .toolbar'):
                    remove.decompose()
                
                text = self.parser._clean_text(content_elem.text)
                if len(text) > 5:  # 최소 길이
                    return text
        
        # 전체 텍스트에서 추출
        text = self.parser._clean_text(comment_elem.text)
        if len(text) > 10:
            return text
        
        return None
    
    def _extract_date(self, comment_elem: BeautifulSoup) -> Optional[datetime]:
        """댓글 날짜 추출"""
        # time 태그
        time_elem = comment_elem.find('time')
        if time_elem and time_elem.get('datetime'):
            try:
                import dateutil.parser
                return dateutil.parser.parse(time_elem['datetime'])
            except:
                pass
        
        # 날짜 관련 클래스
        date_selectors = [
            '.date', '.time', '.timestamp',
            '[class*="date"]', '[class*="time"]'
        ]
        
        for selector in date_selectors:
            date_elem = comment_elem.select_one(selector)
            if date_elem:
                date_text = self.parser._clean_text(date_elem.text)
                try:
                    import dateutil.parser
                    return dateutil.parser.parse(date_text)
                except:
                    pass
        
        return None
    
    def _extract_likes(self, comment_elem: BeautifulSoup) -> int:
        """좋아요 수 추출"""
        like_selectors = [
            '.likes', '.like-count', '.vote-count',
            '[class*="like"]', '[class*="vote"]',
            '.upvotes'
        ]
        
        for selector in like_selectors:
            like_elem = comment_elem.select_one(selector)
            if like_elem:
                text = self.parser._clean_text(like_elem.text)
                # 숫자 추출
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        
        return 0
    
    def _extract_replies(self, comment_elem: BeautifulSoup) -> List[Dict[str, Any]]:
        """대댓글 추출"""
        replies = []
        
        # 대댓글 영역
        reply_areas = comment_elem.select('.replies, .children, .comment-children')
        
        for area in reply_areas:
            # 재귀적으로 댓글 추출
            for reply_elem in self._find_comments(area):
                reply_data = self._extract_single_comment(reply_elem)
                if reply_data:
                    replies.append(reply_data)
        
        return replies
    
    def _is_reply(self, comment_elem: BeautifulSoup) -> bool:
        """대댓글인지 확인"""
        # 클래스 확인
        if comment_elem.get('class'):
            classes = ' '.join(comment_elem['class'])
            if any(word in classes for word in ['reply', 'child', 'nested']):
                return True
        
        # 부모 요소 확인
        parent = comment_elem.parent
        if parent and parent.get('class'):
            classes = ' '.join(parent['class'])
            if any(word in classes for word in ['replies', 'children']):
                return True
        
        # 들여쓰기 레벨 확인
        style = comment_elem.get('style', '')
        if 'margin-left' in style or 'padding-left' in style:
            return True
        
        return False
    
    def _extract_parent_id(self, comment_elem: BeautifulSoup) -> Optional[str]:
        """부모 댓글 ID 추출"""
        # data 속성
        for attr in ['data-parent-id', 'data-reply-to']:
            if comment_elem.get(attr):
                return comment_elem[attr]
        
        # 부모 댓글 요소 찾기
        parent = comment_elem.find_parent(self.single_comment_selectors)
        if parent:
            return self._extract_comment_id(parent)
        
        return None
    
    def extract_ajax_endpoint(self, soup: BeautifulSoup) -> Optional[str]:
        """AJAX 댓글 로딩 엔드포인트 추출"""
        # 스크립트에서 찾기
        scripts = soup.find_all('script')
        
        patterns = [
            r'commentUrl\s*[:=]\s*["\']([^"\']+)',
            r'loadComments\s*\(["\']([^"\']+)',
            r'ajax.*comment.*url\s*[:=]\s*["\']([^"\']+)'
        ]
        
        for script in scripts:
            if script.string:
                for pattern in patterns:
                    match = re.search(pattern, script.string, re.I)
                    if match:
                        return match.group(1)
        
        # data 속성에서 찾기
        comment_area = self._find_comment_area(soup)
        if comment_area:
            for attr in ['data-url', 'data-ajax-url', 'data-load-url']:
                if comment_area.get(attr):
                    return comment_area[attr]
        
        return None
    
    def parse_json_comments(self, json_data: Union[str, dict]) -> List[Dict[str, Any]]:
        """JSON 형식 댓글 파싱"""
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except:
                return []
        else:
            data = json_data
        
        comments = []
        
        # 일반적인 JSON 구조
        if isinstance(data, dict):
            # 댓글 목록 찾기
            for key in ['comments', 'data', 'items', 'results']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        comment = self._parse_json_comment(item)
                        if comment:
                            comments.append(comment)
                    break
        
        elif isinstance(data, list):
            for item in data:
                comment = self._parse_json_comment(item)
                if comment:
                    comments.append(comment)
        
        return comments
    
    def _parse_json_comment(self, item: dict) -> Optional[Dict[str, Any]]:
        """JSON 댓글 아이템 파싱"""
        try:
            # 일반적인 필드 매핑
            field_mappings = {
                'id': ['id', 'comment_id', 'cid'],
                'author': ['author', 'user', 'username', 'name'],
                'content': ['content', 'text', 'message', 'comment'],
                'date': ['date', 'created', 'timestamp', 'created_at'],
                'likes': ['likes', 'votes', 'score', 'like_count']
            }
            
            comment = {}
            
            for field, possible_keys in field_mappings.items():
                for key in possible_keys:
                    if key in item:
                        if field == 'author' and isinstance(item[key], dict):
                            # 중첩된 사용자 객체
                            comment[field] = item[key].get('name') or item[key].get('username')
                        elif field == 'date':
                            # 날짜 파싱
                            try:
                                import dateutil.parser
                                comment[field] = dateutil.parser.parse(item[key])
                            except:
                                comment[field] = item[key]
                        else:
                            comment[field] = item[key]
                        break
            
            # 대댓글
            if 'replies' in item or 'children' in item:
                replies_data = item.get('replies') or item.get('children')
                if isinstance(replies_data, list):
                    comment['replies'] = [
                        self._parse_json_comment(r) for r in replies_data
                        if isinstance(r, dict)
                    ]
            
            return comment if comment.get('content') else None
            
        except Exception as e:
            self.logger.debug(f"Error parsing JSON comment: {e}")
            return None