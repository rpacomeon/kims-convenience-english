"""SM-2 간격반복 알고리즘 및 학습 데이터 관리

망각곡선 기반 복습 일정 자동 계산
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class SM2Algorithm:
    """SM-2 간격반복 알고리즘 구현"""

    @staticmethod
    def calculate_next_interval(
        quality: int,
        repetitions: int,
        ease_factor: float,
        interval: int
    ) -> tuple[int, float, int]:
        """다음 복습 간격을 계산한다.

        Args:
            quality: 답변 품질 (0=완전 망각 ~ 5=완벽)
            repetitions: 현재까지 반복 횟수
            ease_factor: 난이도 계수 (기본 2.5, 최소 1.3)
            interval: 현재 간격 (일)

        Returns:
            (new_interval, new_ease_factor, new_repetitions)

        SM-2 알고리즘:
        - quality < 3: 처음부터 (interval=1, repetitions=0)
        - quality >= 3:
          - rep=0: interval=1
          - rep=1: interval=6
          - rep>=2: interval = 이전 interval * ease_factor
        - ease_factor 조정: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        """
        # quality가 3 미만이면 처음부터 시작
        if quality < 3:
            return 1, ease_factor, 0

        # ease_factor 업데이트
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)  # 최소값 1.3

        # 반복 횟수 증가
        new_repetitions = repetitions + 1

        # 간격 계산
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * new_ease_factor)

        return new_interval, new_ease_factor, new_repetitions


class LearningDataManager:
    """학습 데이터 관리 클래스"""

    def __init__(self, data_path: str | Path = "learning_data.json"):
        """
        Args:
            data_path: 학습 데이터 JSON 파일 경로
        """
        self.data_path = Path(data_path)
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """학습 데이터를 로드한다.

        Returns:
            학습 데이터 딕셔너리

        구조:
        {
            "expressions": {
                "expression_id": {
                    "text": "표현 텍스트",
                    "ease_factor": 2.5,
                    "interval": 1,
                    "repetitions": 0,
                    "next_review": "2024-01-15",
                    "last_review": "2024-01-14",
                    "quality_history": [4, 5, 3],
                    "created_at": "2024-01-01"
                }
            },
            "statistics": {
                "total_reviews": 0,
                "correct_rate": 0.0
            }
        }
        """
        if not self.data_path.exists():
            return {
                "expressions": {},
                "statistics": {
                    "total_reviews": 0,
                    "correct_rate": 0.0,
                    "total_expressions": 0
                }
            }

        with open(self.data_path, encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self):
        """학습 데이터를 저장한다."""
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_expression(self, expression_id: str, text: str, metadata: Optional[dict] = None):
        """새로운 표현을 추가한다.

        Args:
            expression_id: 표현 고유 ID
            text: 표현 텍스트
            metadata: 추가 메타데이터 (episode, category 등)
        """
        if expression_id in self.data["expressions"]:
            return  # 이미 존재

        self.data["expressions"][expression_id] = {
            "text": text,
            "ease_factor": 2.5,
            "interval": 1,
            "repetitions": 0,
            "next_review": datetime.now().strftime("%Y-%m-%d"),
            "last_review": None,
            "quality_history": [],
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "metadata": metadata or {}
        }

        self.data["statistics"]["total_expressions"] = len(self.data["expressions"])
        self._save_data()

    def record_review(self, expression_id: str, quality: int):
        """복습 결과를 기록하고 다음 복습 일정을 계산한다.

        Args:
            expression_id: 표현 ID
            quality: 답변 품질 (0~5)

        Raises:
            KeyError: 표현이 존재하지 않을 때
        """
        if expression_id not in self.data["expressions"]:
            raise KeyError(f"표현을 찾을 수 없습니다: {expression_id}")

        expr = self.data["expressions"][expression_id]

        # SM-2 알고리즘으로 다음 간격 계산
        new_interval, new_ease_factor, new_repetitions = SM2Algorithm.calculate_next_interval(
            quality=quality,
            repetitions=expr["repetitions"],
            ease_factor=expr["ease_factor"],
            interval=expr["interval"]
        )

        # 다음 복습 날짜 계산
        next_review = datetime.now() + timedelta(days=new_interval)

        # 데이터 업데이트
        expr["interval"] = new_interval
        expr["ease_factor"] = new_ease_factor
        expr["repetitions"] = new_repetitions
        expr["next_review"] = next_review.strftime("%Y-%m-%d")
        expr["last_review"] = datetime.now().strftime("%Y-%m-%d")
        expr["quality_history"].append(quality)

        # 통계 업데이트
        self.data["statistics"]["total_reviews"] += 1
        total_quality = sum(
            sum(e["quality_history"])
            for e in self.data["expressions"].values()
        )
        total_count = sum(
            len(e["quality_history"])
            for e in self.data["expressions"].values()
        )
        self.data["statistics"]["correct_rate"] = (
            (total_quality / (total_count * 5)) if total_count > 0 else 0.0
        )

        self._save_data()

    def get_due_expressions(self, date: Optional[str] = None) -> list[dict]:
        """특정 날짜에 복습해야 할 표현 목록을 가져온다.

        Args:
            date: 날짜 (YYYY-MM-DD), None이면 오늘

        Returns:
            복습 대상 표현 리스트 [{"id": "...", "text": "...", "days_overdue": 1}, ...]
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        target_date = datetime.strptime(date, "%Y-%m-%d")
        due_list = []

        for expr_id, expr in self.data["expressions"].items():
            next_review = datetime.strptime(expr["next_review"], "%Y-%m-%d")

            if next_review <= target_date:
                days_overdue = (target_date - next_review).days
                due_list.append({
                    "id": expr_id,
                    "text": expr["text"],
                    "days_overdue": days_overdue,
                    "metadata": expr.get("metadata", {})
                })

        # 연체 일수 순으로 정렬 (오래된 것 우선)
        due_list.sort(key=lambda x: x["days_overdue"], reverse=True)
        return due_list

    def get_statistics(self) -> dict:
        """학습 통계를 가져온다.

        Returns:
            통계 딕셔너리
        """
        return self.data["statistics"]

    def get_expression(self, expression_id: str) -> Optional[dict]:
        """특정 표현의 학습 데이터를 가져온다.

        Args:
            expression_id: 표현 ID

        Returns:
            표현 데이터, 없으면 None
        """
        return self.data["expressions"].get(expression_id)


if __name__ == "__main__":
    # 테스트 코드
    print("=== SM-2 간격반복 알고리즘 테스트 ===\n")

    # 1. 알고리즘 테스트
    print("[OK] SM-2 알고리즘 테스트:")
    test_cases = [
        (5, 0, 2.5, 1, "완벽한 답변 (첫 복습)"),
        (4, 1, 2.6, 1, "좋은 답변 (두 번째 복습)"),
        (3, 2, 2.5, 6, "보통 답변 (세 번째 복습)"),
        (2, 3, 2.4, 15, "어려운 답변 (네 번째 복습 - 리셋됨)"),
    ]

    for quality, reps, ef, interval, desc in test_cases:
        new_interval, new_ef, new_reps = SM2Algorithm.calculate_next_interval(
            quality, reps, ef, interval
        )
        print(f"  {desc}")
        print(f"    Q={quality}, R={reps} -> 다음: {new_interval}일 후, EF={new_ef:.2f}, R={new_reps}")

    # 2. 학습 데이터 관리자 테스트
    print("\n[OK] 학습 데이터 관리자 테스트:")

    import tempfile
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir) / "test_learning_data.json"

    manager = LearningDataManager(temp_path)

    # 표현 추가
    manager.add_expression("expr_001", "How are you?", {"episode": 1, "category": "greetings"})
    manager.add_expression("expr_002", "Thank you very much.", {"episode": 1, "category": "greetings"})
    manager.add_expression("expr_003", "Can you help me?", {"episode": 2, "category": "requests"})

    print(f"  표현 3개 추가 완료")
    print(f"  통계: {manager.get_statistics()}")

    # 복습 기록
    print("\n  복습 시뮬레이션:")
    manager.record_review("expr_001", quality=5)  # 완벽
    expr = manager.get_expression("expr_001")
    print(f"    expr_001 복습 (Q=5) -> 다음: {expr['interval']}일 후 ({expr['next_review']})")

    manager.record_review("expr_002", quality=3)  # 보통
    expr = manager.get_expression("expr_002")
    print(f"    expr_002 복습 (Q=3) -> 다음: {expr['interval']}일 후 ({expr['next_review']})")

    # 복습 대상 확인
    due = manager.get_due_expressions()
    print(f"\n  오늘 복습 대상: {len(due)}개")
    for item in due:
        print(f"    - {item['text']} (연체 {item['days_overdue']}일)")

    # 정리
    Path(temp_path).unlink()
    print("\n[OK] 테스트 완료!")
