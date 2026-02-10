"""30일 커리큘럼 모듈

에피소드 13개를 4주에 분배, 매일 학습 계획 생성
"""

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


# 30일 커리큘럼 매핑
# Week 1 (Day 1-7): Episode 1-3
# Week 2 (Day 8-14): Episode 4-6
# Week 3 (Day 15-21): Episode 7-10
# Week 4 (Day 22-30): Episode 11-13 + 종합 복습

CURRICULUM_MAP = {
    # Week 1
    1: {"episodes": [1], "focus": "기초 인사, 가게 표현", "phrasal_verbs": ["come in", "pick up", "put up"]},
    2: {"episodes": [1], "focus": "소개 표현, 질문하기", "phrasal_verbs": ["look for", "find out"]},
    3: {"episodes": [2], "focus": "일상 대화, 부탁하기", "phrasal_verbs": ["help out", "work out"]},
    4: {"episodes": [2], "focus": "감정 표현, 공감하기", "phrasal_verbs": ["cheer up", "calm down"]},
    5: {"episodes": [3], "focus": "가족 대화, 조언하기", "phrasal_verbs": ["get along", "hang out"]},
    6: {"episodes": [3], "focus": "의견 나누기, 동의/반대", "phrasal_verbs": ["go on", "come on"]},
    7: {"episodes": [1, 2, 3], "focus": "Week 1 복습", "phrasal_verbs": []},

    # Week 2
    8: {"episodes": [4], "focus": "직장 대화, 업무 표현", "phrasal_verbs": ["take over", "hand in"]},
    9: {"episodes": [4], "focus": "계획 세우기, 약속하기", "phrasal_verbs": ["set up", "plan out"]},
    10: {"episodes": [5], "focus": "문제 해결, 제안하기", "phrasal_verbs": ["figure out", "work out"]},
    11: {"episodes": [5], "focus": "거절하기, 사과하기", "phrasal_verbs": ["turn down", "call off"]},
    12: {"episodes": [6], "focus": "관계 표현, 우정", "phrasal_verbs": ["get along", "catch up"]},
    13: {"episodes": [6], "focus": "감사 표현, 칭찬하기", "phrasal_verbs": ["show up", "count on"]},
    14: {"episodes": [4, 5, 6], "focus": "Week 2 복습", "phrasal_verbs": []},

    # Week 3
    15: {"episodes": [7], "focus": "고민 상담, 위로하기", "phrasal_verbs": ["get over", "move on"]},
    16: {"episodes": [7], "focus": "격려하기, 응원하기", "phrasal_verbs": ["cheer up", "give up"]},
    17: {"episodes": [8], "focus": "의견 충돌, 논쟁", "phrasal_verbs": ["break up", "make up"]},
    18: {"episodes": [8], "focus": "타협하기, 양보하기", "phrasal_verbs": ["give in", "back down"]},
    19: {"episodes": [9], "focus": "계획 변경, 대안 제시", "phrasal_verbs": ["put off", "call off"]},
    20: {"episodes": [9, 10], "focus": "결정하기, 선택하기", "phrasal_verbs": ["think over", "figure out"]},
    21: {"episodes": [7, 8, 9, 10], "focus": "Week 3 복습", "phrasal_verbs": []},

    # Week 4
    22: {"episodes": [11], "focus": "미래 이야기, 희망 표현", "phrasal_verbs": ["look forward", "dream of"]},
    23: {"episodes": [11], "focus": "과거 회상, 추억", "phrasal_verbs": ["look back", "think back"]},
    24: {"episodes": [12], "focus": "변화 표현, 성장", "phrasal_verbs": ["grow up", "change into"]},
    25: {"episodes": [12], "focus": "감사와 사랑 표현", "phrasal_verbs": ["care for", "look after"]},
    26: {"episodes": [13], "focus": "마무리, 작별 인사", "phrasal_verbs": ["say goodbye", "see off"]},
    27: {"episodes": [13], "focus": "전체 에피소드 복습", "phrasal_verbs": []},
    28: {"episodes": [1, 2, 3, 4, 5, 6], "focus": "전반부 종합 복습", "phrasal_verbs": []},
    29: {"episodes": [7, 8, 9, 10, 11, 12, 13], "focus": "후반부 종합 복습", "phrasal_verbs": []},
    30: {"episodes": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], "focus": "전체 최종 복습", "phrasal_verbs": []}
}


class Curriculum:
    """30일 커리큘럼 관리 클래스"""

    def __init__(self, df: pd.DataFrame, start_date: Optional[str] = None):
        """
        Args:
            df: 전체 자막 DataFrame
            start_date: 시작 날짜 (YYYY-MM-DD), None이면 오늘
        """
        self.df = df
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()

    def get_current_day(self, date: Optional[str] = None) -> int:
        """현재 진행 일자를 계산한다.

        Args:
            date: 날짜 (YYYY-MM-DD), None이면 오늘

        Returns:
            Day 번호 (1~30+)
        """
        if date is None:
            current_date = datetime.now()
        else:
            current_date = datetime.strptime(date, "%Y-%m-%d")

        days_diff = (current_date - self.start_date).days + 1
        return max(1, days_diff)

    def get_day_plan(self, day: int) -> dict:
        """특정 일자의 학습 계획을 가져온다.

        Args:
            day: Day 번호 (1~30)

        Returns:
            학습 계획 딕셔너리
            {
                "day": 1,
                "episodes": [1],
                "focus": "기초 인사, 가게 표현",
                "phrasal_verbs": ["come in", "pick up"],
                "expressions": [...],  # DataFrame
                "new_count": 15,
                "review_count": 0
            }
        """
        # 30일 초과 시 30일 계획 반환
        if day > 30:
            day = 30

        plan = CURRICULUM_MAP.get(day, CURRICULUM_MAP[30])

        # 해당 에피소드 표현 가져오기
        episodes = plan["episodes"]

        if 'episode' not in self.df.columns:
            from data_loader import add_episode_column
            self.df = add_episode_column(self.df)

        if 'clean_subtitle' not in self.df.columns:
            from data_loader import add_clean_subtitle_column
            self.df = add_clean_subtitle_column(self.df)

        # 에피소드 필터링
        episode_df = self.df[self.df['episode'].isin(episodes)].copy()

        # 핵심 표현 추출 (복습일이 아니면)
        if "복습" in plan["focus"]:
            # 복습일: 모든 에피소드의 high-quality 표현
            from expression_extractor import filter_useful_lines, calculate_sentence_quality

            useful = filter_useful_lines(episode_df)
            useful['quality_score'] = useful['clean_subtitle'].apply(calculate_sentence_quality)
            expressions = useful.nlargest(30, 'quality_score')
            new_count = 0
            review_count = len(expressions)
        else:
            # 일반 학습일: 에피소드별 핵심 표현
            from expression_extractor import extract_key_expressions

            expressions_list = []
            for ep in episodes:
                ep_expr = extract_key_expressions(self.df, episode=ep, top_n=15)
                expressions_list.append(ep_expr)

            if expressions_list:
                expressions = pd.concat(expressions_list, ignore_index=True)
            else:
                expressions = pd.DataFrame()

            new_count = len(expressions)
            review_count = 0

        return {
            "day": day,
            "week": (day - 1) // 7 + 1,
            "episodes": episodes,
            "focus": plan["focus"],
            "phrasal_verbs": plan["phrasal_verbs"],
            "expressions": expressions,
            "new_count": new_count,
            "review_count": review_count,
            "is_review_day": "복습" in plan["focus"]
        }

    def get_today_plan(self) -> dict:
        """오늘의 학습 계획을 가져온다.

        Returns:
            학습 계획 딕셔너리
        """
        day = self.get_current_day()
        return self.get_day_plan(day)

    def get_week_summary(self, week: int) -> dict:
        """특정 주의 요약을 가져온다.

        Args:
            week: 주차 (1~4)

        Returns:
            주간 요약 딕셔너리
            {
                "week": 1,
                "days": [1, 2, 3, 4, 5, 6, 7],
                "episodes": [1, 2, 3],
                "total_expressions": 100
            }
        """
        start_day = (week - 1) * 7 + 1
        end_day = min(week * 7, 30)

        days = list(range(start_day, end_day + 1))
        all_episodes = set()

        for day in days:
            plan = CURRICULUM_MAP.get(day, {})
            all_episodes.update(plan.get("episodes", []))

        return {
            "week": week,
            "days": days,
            "episodes": sorted(list(all_episodes)),
            "description": f"Week {week} 학습"
        }

    def get_progress(self, current_day: Optional[int] = None) -> dict:
        """학습 진행률을 계산한다.

        Args:
            current_day: 현재 일자, None이면 자동 계산

        Returns:
            진행률 딕셔너리
            {
                "current_day": 5,
                "total_days": 30,
                "progress_percent": 16.7,
                "completed_episodes": [1, 2],
                "remaining_episodes": [3, 4, 5, ...]
            }
        """
        if current_day is None:
            current_day = self.get_current_day()

        # 현재까지 학습한 에피소드
        completed_episodes = set()
        for day in range(1, current_day):
            plan = CURRICULUM_MAP.get(day, {})
            completed_episodes.update(plan.get("episodes", []))

        # 남은 에피소드
        all_episodes = set(range(1, 14))
        remaining_episodes = all_episodes - completed_episodes

        progress_percent = (current_day / 30) * 100

        return {
            "current_day": current_day,
            "total_days": 30,
            "progress_percent": min(100.0, progress_percent),
            "completed_episodes": sorted(list(completed_episodes)),
            "remaining_episodes": sorted(list(remaining_episodes))
        }


if __name__ == "__main__":
    # 테스트 코드
    print("=== 30일 커리큘럼 테스트 ===\n")

    from data_loader import load_subtitle_data, add_episode_column, add_clean_subtitle_column

    # 데이터 로드
    df = load_subtitle_data("../김씨네 편의점.txt")
    df = add_episode_column(df)
    df = add_clean_subtitle_column(df)

    # 커리큘럼 생성 (오늘 시작)
    curriculum = Curriculum(df)

    # 1. 오늘의 계획
    print("[OK] 오늘의 학습 계획:")
    today = curriculum.get_today_plan()
    print(f"  Day {today['day']} (Week {today['week']})")
    print(f"  에피소드: {today['episodes']}")
    print(f"  학습 초점: {today['focus']}")
    print(f"  구동사: {', '.join(today['phrasal_verbs']) if today['phrasal_verbs'] else '없음'}")
    print(f"  새 표현: {today['new_count']}개")
    print(f"  복습: {today['review_count']}개")

    # 2. 특정 Day 계획
    print("\n[OK] Day 7 (Week 1 복습):")
    day7 = curriculum.get_day_plan(7)
    print(f"  에피소드: {day7['episodes']}")
    print(f"  학습 초점: {day7['focus']}")
    print(f"  복습일: {day7['is_review_day']}")

    # 3. Week 1 요약
    print("\n[OK] Week 1 요약:")
    week1 = curriculum.get_week_summary(1)
    print(f"  Day: {week1['days']}")
    print(f"  에피소드: {week1['episodes']}")

    # 4. 진행률
    print("\n[OK] 학습 진행률:")
    progress = curriculum.get_progress()
    print(f"  현재: Day {progress['current_day']}/{progress['total_days']}")
    print(f"  진행률: {progress['progress_percent']:.1f}%")
    print(f"  완료 에피소드: {progress['completed_episodes']}")
    print(f"  남은 에피소드: {progress['remaining_episodes']}")

    # 5. 30일 전체 커리큘럼 요약
    print("\n[OK] 30일 커리큘럼 요약:")
    for week in range(1, 5):
        summary = curriculum.get_week_summary(week)
        print(f"  Week {week}: Episode {summary['episodes']}")

    print("\n[OK] 테스트 완료!")
