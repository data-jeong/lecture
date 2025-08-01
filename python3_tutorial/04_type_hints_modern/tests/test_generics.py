"""
Generic 타입 테스트
"""

import pytest
from datetime import datetime
from todo_app.types.generics import Result, Option, Cache, Page

class TestResult:
    """Result 타입 테스트"""
    
    def test_ok_result(self):
        """성공 결과 테스트"""
        result = Result.ok("success")
        
        assert result.is_ok()
        assert not result.is_err()
        assert result.unwrap() == "success"
        assert result.unwrap_or("default") == "success"
    
    def test_err_result(self):
        """실패 결과 테스트"""
        result = Result.err("error")
        
        assert not result.is_ok()
        assert result.is_err()
        assert result.unwrap_err() == "error"
        assert result.unwrap_or("default") == "default"
    
    def test_unwrap_panic(self):
        """unwrap 실패 테스트"""
        result = Result.err("error")
        
        with pytest.raises(ValueError, match="Called unwrap on an Err value"):
            result.unwrap()
    
    def test_unwrap_err_panic(self):
        """unwrap_err 실패 테스트"""
        result = Result.ok("success")
        
        with pytest.raises(ValueError, match="Called unwrap_err on an Ok value"):
            result.unwrap_err()
    
    def test_map(self):
        """map 함수 테스트"""
        ok_result = Result.ok(5)
        err_result = Result.err("error")
        
        mapped_ok = ok_result.map(lambda x: x * 2)
        mapped_err = err_result.map(lambda x: x * 2)
        
        assert mapped_ok.is_ok()
        assert mapped_ok.unwrap() == 10
        
        assert mapped_err.is_err()
        assert mapped_err.unwrap_err() == "error"
    
    def test_map_err(self):
        """map_err 함수 테스트"""
        ok_result = Result.ok("success")
        err_result = Result.err("error")
        
        mapped_ok = ok_result.map_err(lambda e: f"mapped: {e}")
        mapped_err = err_result.map_err(lambda e: f"mapped: {e}")
        
        assert mapped_ok.is_ok()
        assert mapped_ok.unwrap() == "success"
        
        assert mapped_err.is_err()
        assert mapped_err.unwrap_err() == "mapped: error"

class TestOption:
    """Option 타입 테스트"""
    
    def test_some_option(self):
        """값이 있는 Option 테스트"""
        option = Option.some("value")
        
        assert option.is_some()
        assert not option.is_none()
        assert option.unwrap() == "value"
        assert option.unwrap_or("default") == "value"
    
    def test_none_option(self):
        """값이 없는 Option 테스트"""
        option = Option.none()
        
        assert not option.is_some()
        assert option.is_none()
        assert option.unwrap_or("default") == "default"
    
    def test_unwrap_panic(self):
        """unwrap 실패 테스트"""
        option = Option.none()
        
        with pytest.raises(ValueError, match="Called unwrap on a None value"):
            option.unwrap()
    
    def test_map(self):
        """map 함수 테스트"""
        some_option = Option.some(5)
        none_option = Option.none()
        
        mapped_some = some_option.map(lambda x: x * 2)
        mapped_none = none_option.map(lambda x: x * 2)
        
        assert mapped_some.is_some()
        assert mapped_some.unwrap() == 10
        
        assert mapped_none.is_none()
    
    def test_filter(self):
        """filter 함수 테스트"""
        some_option = Option.some(5)
        
        filtered_true = some_option.filter(lambda x: x > 3)
        filtered_false = some_option.filter(lambda x: x < 3)
        
        assert filtered_true.is_some()
        assert filtered_true.unwrap() == 5
        
        assert filtered_false.is_none()

class TestCache:
    """Cache 타입 테스트"""
    
    def test_cache_operations(self):
        """캐시 기본 동작 테스트"""
        cache = Cache[str, int]()
        
        # 빈 캐시에서 조회
        assert cache.get("key") is None
        
        # 값 저장
        cache.set("key", 42)
        assert cache.get("key") == 42
        
        # 값 무효화
        cache.invalidate("key")
        assert cache.get("key") is None
    
    def test_cache_clear(self):
        """캐시 전체 초기화 테스트"""
        cache = Cache[str, int]()
        
        cache.set("key1", 1)
        cache.set("key2", 2)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

class TestPage:
    """Page 타입 테스트"""
    
    def test_page_properties(self):
        """페이지 속성 테스트"""
        items = list(range(10))
        page = Page(items=items, total=25, page=2, per_page=10)
        
        assert page.total_pages == 3
        assert page.has_next
        assert page.has_prev
    
    def test_first_page(self):
        """첫 페이지 테스트"""
        items = list(range(5))
        page = Page(items=items, total=15, page=1, per_page=5)
        
        assert not page.has_prev
        assert page.has_next
    
    def test_last_page(self):
        """마지막 페이지 테스트"""
        items = list(range(3))
        page = Page(items=items, total=13, page=3, per_page=5)
        
        assert page.has_prev
        assert not page.has_next
    
    def test_single_page(self):
        """단일 페이지 테스트"""
        items = list(range(3))
        page = Page(items=items, total=3, page=1, per_page=10)
        
        assert not page.has_prev
        assert not page.has_next
        assert page.total_pages == 1