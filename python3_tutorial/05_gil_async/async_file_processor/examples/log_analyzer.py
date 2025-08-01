"""
로그 분석 예제
대용량 로그 파일의 스트림 처리
"""

import asyncio
import time
import random
from pathlib import Path
from typing import Dict, List, AsyncIterator, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict, Counter

from ..core.async_processor import AsyncProcessor
from ..patterns.batch_processor import AsyncBatchProcessor, AdaptiveBatchProcessor
from ..patterns.producer_consumer import AsyncProducerConsumer
from ..utils.benchmark import measure_time_async


@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    source: str
    message: str
    ip: Optional[str] = None
    user_id: Optional[int] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "ip": self.ip,
            "user_id": self.user_id,
            "response_time": self.response_time,
            "status_code": self.status_code
        }


@dataclass
class LogAnalysisResult:
    """로그 분석 결과"""
    total_entries: int = 0
    level_counts: Dict[str, int] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    average_response_time: float = 0
    status_code_distribution: Dict[int, int] = field(default_factory=dict)
    top_ips: List[tuple] = field(default_factory=list)
    hourly_distribution: Dict[int, int] = field(default_factory=dict)
    anomalies: List[dict] = field(default_factory=list)


class LogAnalyzerExample:
    """로그 분석 예제"""
    
    def __init__(self):
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] \[([^\]]+)\] (.+)'
        )
        self.ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
        self.response_time_pattern = re.compile(r'response_time=(\d+\.?\d*)ms')
        self.status_pattern = re.compile(r'status=(\d+)')
        self.user_pattern = re.compile(r'user_id=(\d+)')
    
    async def generate_sample_logs(self, output_file: Path, num_entries: int = 10000):
        """샘플 로그 파일 생성"""
        print(f"📝 {num_entries:,}개 로그 엔트리 생성 중...")
        
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        sources = ["web", "api", "database", "auth", "payment"]
        ips = [f"192.168.1.{i}" for i in range(1, 21)]
        
        start_time = datetime.now() - timedelta(hours=24)
        
        with open(output_file, 'w') as f:
            for i in range(num_entries):
                # 시간 증가
                timestamp = start_time + timedelta(seconds=i * 86400 / num_entries)
                
                # 레벨 선택 (가중치)
                level = random.choices(
                    levels,
                    weights=[10, 60, 20, 8, 2],
                    k=1
                )[0]
                
                source = random.choice(sources)
                ip = random.choice(ips)
                user_id = random.randint(1000, 9999) if random.random() > 0.3 else None
                
                # 메시지 생성
                if source == "web":
                    status = random.choices(
                        [200, 201, 400, 404, 500],
                        weights=[70, 10, 10, 8, 2],
                        k=1
                    )[0]
                    response_time = random.gauss(50, 20) if status < 400 else random.gauss(200, 50)
                    response_time = max(1, response_time)
                    
                    message = f"Request from {ip}"
                    if user_id:
                        message += f" user_id={user_id}"
                    message += f" status={status} response_time={response_time:.1f}ms"
                    
                elif source == "database":
                    query_time = random.gauss(10, 5)
                    message = f"Query executed in {query_time:.2f}ms"
                    
                elif source == "auth":
                    action = random.choice(["login", "logout", "token_refresh"])
                    message = f"User {action}"
                    if user_id:
                        message += f" user_id={user_id}"
                    message += f" from {ip}"
                    
                else:
                    message = f"Operation completed from {ip}"
                
                # 에러 메시지 추가
                if level in ["ERROR", "CRITICAL"]:
                    errors = [
                        "Connection timeout",
                        "Database connection failed",
                        "Authentication failed",
                        "Internal server error",
                        "Memory allocation error"
                    ]
                    message += f" - {random.choice(errors)}"
                
                # 로그 라인 작성
                log_line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{level}] [{source}] {message}\n"
                f.write(log_line)
        
        print(f"✅ 로그 파일 생성 완료: {output_file}")
    
    def parse_log_entry(self, line: str) -> Optional[LogEntry]:
        """로그 라인 파싱"""
        match = self.log_pattern.match(line.strip())
        if not match:
            return None
        
        timestamp_str, level, source, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        # 추가 정보 추출
        ip_match = self.ip_pattern.search(message)
        ip = ip_match.group() if ip_match else None
        
        response_time_match = self.response_time_pattern.search(message)
        response_time = float(response_time_match.group(1)) if response_time_match else None
        
        status_match = self.status_pattern.search(message)
        status_code = int(status_match.group(1)) if status_match else None
        
        user_match = self.user_pattern.search(message)
        user_id = int(user_match.group(1)) if user_match else None
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            source=source,
            message=message,
            ip=ip,
            user_id=user_id,
            response_time=response_time,
            status_code=status_code
        )
    
    async def analyze_log_batch(self, entries: List[LogEntry]) -> LogAnalysisResult:
        """로그 배치 분석"""
        result = LogAnalysisResult()
        
        result.total_entries = len(entries)
        
        # 레벨별 카운트
        level_counter = Counter(entry.level for entry in entries)
        result.level_counts = dict(level_counter)
        
        # 에러 메시지 수집
        for entry in entries:
            if entry.level in ["ERROR", "CRITICAL"]:
                result.error_messages.append(entry.message)
        
        # 응답 시간 평균
        response_times = [e.response_time for e in entries if e.response_time]
        if response_times:
            result.average_response_time = sum(response_times) / len(response_times)
        
        # 상태 코드 분포
        status_codes = [e.status_code for e in entries if e.status_code]
        result.status_code_distribution = dict(Counter(status_codes))
        
        # 상위 IP
        ip_counter = Counter(e.ip for e in entries if e.ip)
        result.top_ips = ip_counter.most_common(5)
        
        # 시간대별 분포
        hour_counter = Counter(e.timestamp.hour for e in entries)
        result.hourly_distribution = dict(hour_counter)
        
        # 이상 탐지 (느린 응답)
        for entry in entries:
            if entry.response_time and entry.response_time > 500:
                result.anomalies.append({
                    "type": "slow_response",
                    "timestamp": entry.timestamp.isoformat(),
                    "response_time": entry.response_time,
                    "message": entry.message
                })
        
        return result
    
    async def stream_analyze_logs(self, log_file: Path) -> LogAnalysisResult:
        """로그 파일 스트림 분석"""
        print("\n🔄 로그 파일 스트림 분석 시작...")
        
        # 전체 결과 집계
        total_result = LogAnalysisResult()
        
        # 배치 처리기
        batch_processor = AdaptiveBatchProcessor[LogEntry, LogAnalysisResult](
            initial_batch_size=500,
            min_batch_size=100,
            max_batch_size=2000,
            target_duration=0.5
        )
        
        # 생산자-소비자 패턴
        pc = AsyncProducerConsumer[str, LogEntry](
            max_queue_size=1000,
            num_consumers=4
        )
        
        # 로그 라인 생성기
        async def log_line_generator():
            with open(log_file, 'r') as f:
                for line in f:
                    yield line
                    # 스트리밍 시뮬레이션
                    if random.random() < 0.001:  # 0.1% 확률로 지연
                        await asyncio.sleep(0.01)
        
        # 로그 파싱 함수
        def parse_line(line: str) -> Optional[LogEntry]:
            return self.parse_log_entry(line)
        
        # 파싱 실행
        print("  1️⃣ 로그 파싱 중...")
        parse_results = await pc.run(
            source=log_line_generator(),
            processor=parse_line
        )
        
        # 파싱된 엔트리 추출
        entries = []
        for result in parse_results:
            if "result" in result and result["result"]:
                entries.append(result["result"])
        
        print(f"  ✅ {len(entries):,}개 엔트리 파싱 완료")
        
        # 배치 분석
        print("  2️⃣ 배치 분석 중...")
        
        @measure_time_async
        async def analyze_entries():
            batch_results = await batch_processor.add_many(entries, self.analyze_log_batch)
            return batch_results
        
        batch_results, analysis_time = await analyze_entries()
        
        print(f"  ✅ {len(batch_results)}개 배치로 분석 완료 ({analysis_time:.2f}초)")
        
        # 결과 집계
        for batch_result in batch_results:
            if batch_result.results:
                for result in batch_result.results:
                    # 결과 병합
                    total_result.total_entries += result.total_entries
                    
                    for level, count in result.level_counts.items():
                        total_result.level_counts[level] = \
                            total_result.level_counts.get(level, 0) + count
                    
                    total_result.error_messages.extend(result.error_messages)
                    
                    # 응답 시간 평균 재계산은 단순화
                    if result.average_response_time > 0:
                        total_result.average_response_time = result.average_response_time
                    
                    for code, count in result.status_code_distribution.items():
                        total_result.status_code_distribution[code] = \
                            total_result.status_code_distribution.get(code, 0) + count
                    
                    for hour, count in result.hourly_distribution.items():
                        total_result.hourly_distribution[hour] = \
                            total_result.hourly_distribution.get(hour, 0) + count
                    
                    total_result.anomalies.extend(result.anomalies)
        
        # 상위 IP 재계산
        all_ips = []
        for entry in entries:
            if entry.ip:
                all_ips.append(entry.ip)
        ip_counter = Counter(all_ips)
        total_result.top_ips = ip_counter.most_common(10)
        
        # 배치 처리 통계
        batch_stats = batch_processor.get_statistics()
        print("\n📊 배치 처리 통계:")
        for key, value in batch_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        return total_result
    
    def print_analysis_report(self, result: LogAnalysisResult):
        """분석 리포트 출력"""
        print("\n📊 로그 분석 리포트")
        print("=" * 60)
        
        print(f"\n총 로그 엔트리: {result.total_entries:,}개")
        
        print("\n레벨별 분포:")
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            count = result.level_counts.get(level, 0)
            percentage = count / result.total_entries * 100 if result.total_entries > 0 else 0
            bar = "█" * int(percentage / 2)
            print(f"  {level:8} {count:6,} ({percentage:5.1f}%) {bar}")
        
        print(f"\n평균 응답 시간: {result.average_response_time:.2f}ms")
        
        print("\n상태 코드 분포:")
        for code, count in sorted(result.status_code_distribution.items()):
            percentage = count / sum(result.status_code_distribution.values()) * 100
            print(f"  {code}: {count:,} ({percentage:.1f}%)")
        
        print("\n상위 IP 주소:")
        for ip, count in result.top_ips[:5]:
            print(f"  {ip}: {count:,}회")
        
        print("\n시간대별 활동:")
        for hour in range(24):
            count = result.hourly_distribution.get(hour, 0)
            bar = "█" * int(count / max(result.hourly_distribution.values()) * 20)
            print(f"  {hour:02d}시: {bar} {count:,}")
        
        print(f"\n⚠️  감지된 이상: {len(result.anomalies)}개")
        if result.anomalies:
            print("  최근 5개:")
            for anomaly in result.anomalies[:5]:
                print(f"    - [{anomaly['type']}] {anomaly['timestamp']} "
                      f"응답시간: {anomaly['response_time']}ms")
    
    async def run(self):
        """예제 실행"""
        print("📋 로그 분석 예제")
        print("=" * 60)
        
        # 1. 샘플 로그 생성
        log_file = Path("sample_logs.log")
        await self.generate_sample_logs(log_file, num_entries=50000)
        
        # 2. 스트림 분석
        result = await self.stream_analyze_logs(log_file)
        
        # 3. 리포트 출력
        self.print_analysis_report(result)
        
        # 4. 결과 저장
        print("\n💾 분석 결과 저장...")
        
        report_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_entries": result.total_entries,
            "level_distribution": result.level_counts,
            "average_response_time": result.average_response_time,
            "status_code_distribution": result.status_code_distribution,
            "top_ips": result.top_ips,
            "hourly_distribution": result.hourly_distribution,
            "anomaly_count": len(result.anomalies),
            "sample_anomalies": result.anomalies[:10]
        }
        
        with open("log_analysis_report.json", 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print("  ✅ log_analysis_report.json 저장 완료")
        
        # 에러 로그 별도 저장
        if result.error_messages:
            with open("error_logs.txt", 'w') as f:
                for error in result.error_messages[:100]:  # 최대 100개
                    f.write(error + '\n')
            print("  ✅ error_logs.txt 저장 완료")


async def main():
    """메인 함수"""
    example = LogAnalyzerExample()
    await example.run()


if __name__ == "__main__":
    asyncio.run(main())