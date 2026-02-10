"""퀴즈 엔진 모듈

4종 퀴즈: 한→영, 영→한, 빈칸 채우기, 문법 교정
"""

import random
import re
from typing import Optional

import pandas as pd


class QuizEngine:
    """퀴즈 생성 및 관리 클래스"""

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: 자막 DataFrame (clean_subtitle, Machine Translation 필요)
        """
        self.df = df.copy()

        # 필수 컬럼 확인
        if 'clean_subtitle' not in self.df.columns:
            from data_loader import add_clean_subtitle_column
            self.df = add_clean_subtitle_column(self.df)

    def generate_kr_to_en_quiz(
        self,
        expression_row: pd.Series,
        num_choices: int = 4
    ) -> dict:
        """한국어 → 영어 객관식 퀴즈를 생성한다.

        Args:
            expression_row: 정답 표현 (DataFrame row)
            num_choices: 선택지 개수

        Returns:
            퀴즈 딕셔너리
            {
                "type": "kr_to_en",
                "question": "한국어 문장",
                "choices": ["영어1", "영어2", ...],
                "correct_index": 0,
                "correct_answer": "정답 영어",
                "explanation": "설명"
            }
        """
        correct_english = expression_row['clean_subtitle']
        correct_korean = expression_row.get('Machine Translation', '')

        # 오답 보기 생성 (유사한 길이/난이도)
        wrong_choices = self._generate_wrong_choices(
            expression_row,
            num_choices - 1,
            column='clean_subtitle'
        )

        # 선택지 섞기
        all_choices = [correct_english] + wrong_choices
        random.shuffle(all_choices)
        correct_index = all_choices.index(correct_english)

        return {
            "type": "kr_to_en",
            "question": correct_korean,
            "choices": all_choices,
            "correct_index": correct_index,
            "correct_answer": correct_english,
            "explanation": f"'{correct_korean}'의 영어 표현은 '{correct_english}'입니다."
        }

    def generate_en_to_kr_quiz(
        self,
        expression_row: pd.Series,
        num_choices: int = 4
    ) -> dict:
        """영어 → 한국어 객관식 퀴즈를 생성한다.

        Args:
            expression_row: 정답 표현 (DataFrame row)
            num_choices: 선택지 개수

        Returns:
            퀴즈 딕셔너리
        """
        correct_english = expression_row['clean_subtitle']
        correct_korean = expression_row.get('Machine Translation', '')

        # 오답 보기 생성
        wrong_choices = self._generate_wrong_choices(
            expression_row,
            num_choices - 1,
            column='Machine Translation'
        )

        # 선택지 섞기
        all_choices = [correct_korean] + wrong_choices
        random.shuffle(all_choices)
        correct_index = all_choices.index(correct_korean)

        return {
            "type": "en_to_kr",
            "question": correct_english,
            "choices": all_choices,
            "correct_index": correct_index,
            "correct_answer": correct_korean,
            "explanation": f"'{correct_english}'의 한국어 뜻은 '{correct_korean}'입니다."
        }

    def generate_fill_blank_quiz(
        self,
        expression_row: pd.Series
    ) -> Optional[dict]:
        """빈칸 채우기 퀴즈를 생성한다.

        핵심 동사/형용사를 빈칸으로 만든다.

        Args:
            expression_row: 정답 표현 (DataFrame row)

        Returns:
            퀴즈 딕셔너리, 생성 실패 시 None
        """
        text = expression_row['clean_subtitle']
        korean = expression_row.get('Machine Translation', '')

        # 핵심 단어 찾기 (동사, 형용사, 중요 명사)
        # 간단한 패턴: 3~10자 단어, 특수 동사/형용사 우선
        key_words_pattern = r'\b(get|go|come|take|put|make|think|know|want|need|like|love|have|help|work|feel|look|seem|happy|good|bad|sorry|right|important|nice|great)\b'

        match = re.search(key_words_pattern, text, re.IGNORECASE)

        if not match:
            # 패턴 매칭 실패 시 3~10자 단어 중 선택
            words = re.findall(r'\b\w{3,10}\b', text)
            if not words:
                return None
            key_word = random.choice(words)
        else:
            key_word = match.group(0)

        # 빈칸 문장 생성
        blank_text = text.replace(key_word, "_____", 1)  # 첫 번째만 교체

        # 선택지 생성 (정답 + 유사 단어)
        similar_words = self._generate_similar_words(key_word, num=3)
        choices = [key_word] + similar_words
        random.shuffle(choices)
        correct_index = choices.index(key_word)

        return {
            "type": "fill_blank",
            "question": blank_text,
            "hint": f"({korean})",
            "choices": choices,
            "correct_index": correct_index,
            "correct_answer": key_word,
            "explanation": f"정답은 '{key_word}'입니다. 완전한 문장: '{text}'"
        }

    def generate_grammar_correction_quiz(
        self,
        broken_row: pd.Series,
        broken_detector
    ) -> Optional[dict]:
        """문법 교정 퀴즈를 생성한다.

        Mr. Kim의 비문법 표현을 올바른 문법으로 고치는 문제.

        Args:
            broken_row: 비문법이 포함된 표현 (DataFrame row)
            broken_detector: BrokenEnglishDetector 인스턴스

        Returns:
            퀴즈 딕셔너리, 비문법이 없으면 None
        """
        text = broken_row['clean_subtitle']
        korean = broken_row.get('Machine Translation', '')

        # 비문법 감지
        result = broken_detector.suggest_correction(text)

        if not result["has_errors"]:
            return None  # 문법 오류 없음

        # 정답: 교정된 문장
        correct_text = result["corrected"]

        # 오답 보기 생성 (원문 + 다른 잘못된 교정)
        wrong_choices = [
            text,  # 원문 (틀린 답)
            self._generate_fake_correction(text, result["issues"]),
            self._generate_fake_correction(text, result["issues"])
        ]

        # 중복 제거
        wrong_choices = list(set(wrong_choices))
        wrong_choices = [c for c in wrong_choices if c != correct_text][:3]

        # 선택지 섞기
        all_choices = [correct_text] + wrong_choices
        random.shuffle(all_choices)
        correct_index = all_choices.index(correct_text)

        # 설명 생성
        explanation = f"원문: '{text}'\n"
        explanation += f"정답: '{correct_text}'\n"
        explanation += "문법 포인트:\n"
        for issue in result["issues"]:
            explanation += f"  - {issue['explanation']}\n"

        return {
            "type": "grammar_correction",
            "question": f"다음 문장의 올바른 표현은? (원문: {text})",
            "hint": f"({korean})",
            "choices": all_choices,
            "correct_index": correct_index,
            "correct_answer": correct_text,
            "explanation": explanation
        }

    def _generate_wrong_choices(
        self,
        correct_row: pd.Series,
        num_wrong: int,
        column: str
    ) -> list[str]:
        """오답 보기를 생성한다.

        Args:
            correct_row: 정답 row
            num_wrong: 오답 개수
            column: 선택할 컬럼명

        Returns:
            오답 리스트
        """
        correct_text = correct_row[column]
        correct_len = len(correct_text.split())

        # 유사한 길이의 다른 표현들 찾기
        candidates = self.df[self.df[column] != correct_text].copy()

        # 길이 유사도 계산
        candidates['len_diff'] = candidates[column].apply(
            lambda x: abs(len(x.split()) - correct_len)
        )

        # 길이 차이 적은 순으로 정렬
        candidates = candidates.sort_values('len_diff')

        # 상위에서 랜덤 샘플링
        sample_pool = candidates.head(50) if len(candidates) >= 50 else candidates
        num_available = min(num_wrong, len(sample_pool))

        if num_available == 0:
            return []

        wrong_samples = sample_pool.sample(num_available)
        return wrong_samples[column].tolist()

    def _generate_similar_words(self, word: str, num: int = 3) -> list[str]:
        """유사한 단어를 생성한다 (간단한 버전).

        Args:
            word: 기준 단어
            num: 생성할 개수

        Returns:
            유사 단어 리스트
        """
        # 동사 그룹
        verb_groups = {
            'get': ['have', 'take', 'make'],
            'go': ['come', 'move', 'walk'],
            'make': ['create', 'build', 'form'],
            'think': ['believe', 'consider', 'suppose'],
            'know': ['understand', 'realize', 'recognize'],
            'want': ['need', 'wish', 'desire'],
            'like': ['love', 'enjoy', 'prefer'],
            'have': ['own', 'possess', 'hold'],
            'help': ['assist', 'support', 'aid'],
            'work': ['function', 'operate', 'perform']
        }

        # 형용사 그룹
        adj_groups = {
            'happy': ['glad', 'pleased', 'joyful'],
            'good': ['nice', 'fine', 'great'],
            'bad': ['poor', 'wrong', 'terrible'],
            'sorry': ['apologetic', 'regretful', 'sad'],
            'important': ['significant', 'crucial', 'vital']
        }

        word_lower = word.lower()

        # 그룹에서 찾기
        if word_lower in verb_groups:
            similar = verb_groups[word_lower]
        elif word_lower in adj_groups:
            similar = adj_groups[word_lower]
        else:
            # 기본: 길이 유사한 단어
            similar = ['good', 'make', 'take', 'know', 'think', 'want', 'need', 'help']

        # 정답 제외하고 샘플링
        similar = [w for w in similar if w.lower() != word_lower]
        return random.sample(similar, min(num, len(similar)))

    def _generate_fake_correction(self, text: str, issues: list) -> str:
        """가짜 교정문을 생성한다 (일부만 교정).

        Args:
            text: 원문
            issues: 감지된 문법 이슈 리스트

        Returns:
            일부만 교정된 문장
        """
        if not issues:
            return text

        # 랜덤하게 일부 이슈만 교정
        num_to_fix = random.randint(1, max(1, len(issues) - 1))
        issues_to_fix = random.sample(issues, num_to_fix)

        corrected = text
        for issue in issues_to_fix:
            corrected = (
                corrected[:issue["start"]] +
                issue["correction"] +
                corrected[issue["end"]:]
            )

        return corrected

    def generate_quiz(
        self,
        quiz_type: str,
        expression_row: Optional[pd.Series] = None,
        broken_detector = None
    ) -> Optional[dict]:
        """퀴즈를 생성한다.

        Args:
            quiz_type: 퀴즈 유형 ("kr_to_en", "en_to_kr", "fill_blank", "grammar_correction", "random")
            expression_row: 표현 row (None이면 랜덤 선택)
            broken_detector: BrokenEnglishDetector (grammar_correction 시 필요)

        Returns:
            퀴즈 딕셔너리, 생성 실패 시 None
        """
        # 랜덤 표현 선택
        if expression_row is None:
            expression_row = self.df.sample(1).iloc[0]

        # 랜덤 유형 선택
        if quiz_type == "random":
            quiz_type = random.choice(["kr_to_en", "en_to_kr", "fill_blank", "grammar_correction"])

        # 유형별 생성
        if quiz_type == "kr_to_en":
            return self.generate_kr_to_en_quiz(expression_row)

        elif quiz_type == "en_to_kr":
            return self.generate_en_to_kr_quiz(expression_row)

        elif quiz_type == "fill_blank":
            return self.generate_fill_blank_quiz(expression_row)

        elif quiz_type == "grammar_correction":
            if broken_detector is None:
                return None
            return self.generate_grammar_correction_quiz(expression_row, broken_detector)

        return None


if __name__ == "__main__":
    # 테스트 코드
    print("=== 퀴즈 엔진 테스트 ===\n")

    from data_loader import load_subtitle_data, add_episode_column, add_clean_subtitle_column
    from broken_english import BrokenEnglishDetector

    # 데이터 로드
    df = load_subtitle_data("../김씨네 편의점.txt")
    df = add_episode_column(df)
    df = add_clean_subtitle_column(df)

    # 퀴즈 엔진 생성
    quiz_engine = QuizEngine(df)
    broken_detector = BrokenEnglishDetector("../config/broken_patterns.json")

    # 1. 한→영 퀴즈
    print("[OK] 한국어 -> 영어 퀴즈:")
    sample = df[df['episode'] == 1].sample(1).iloc[0]
    quiz = quiz_engine.generate_kr_to_en_quiz(sample)
    print(f"  질문: {quiz['question']}")
    for i, choice in enumerate(quiz['choices']):
        mark = " <-- 정답" if i == quiz['correct_index'] else ""
        print(f"    {i+1}. {choice}{mark}")

    # 2. 영→한 퀴즈
    print("\n[OK] 영어 -> 한국어 퀴즈:")
    quiz = quiz_engine.generate_en_to_kr_quiz(sample)
    print(f"  질문: {quiz['question']}")
    for i, choice in enumerate(quiz['choices']):
        mark = " <-- 정답" if i == quiz['correct_index'] else ""
        print(f"    {i+1}. {choice}{mark}")

    # 3. 빈칸 채우기
    print("\n[OK] 빈칸 채우기 퀴즈:")
    quiz = quiz_engine.generate_fill_blank_quiz(sample)
    if quiz:
        print(f"  질문: {quiz['question']}")
        print(f"  힌트: {quiz['hint']}")
        for i, choice in enumerate(quiz['choices']):
            mark = " <-- 정답" if i == quiz['correct_index'] else ""
            print(f"    {i+1}. {choice}{mark}")
    else:
        print("  (생성 실패)")

    # 4. 문법 교정
    print("\n[OK] 문법 교정 퀴즈:")
    # Mr. Kim의 비문법 표현 찾기
    broken_samples = df[df['clean_subtitle'].str.contains(r'\b(you is|how I can|I not|they is)\b', case=False, regex=True)]
    if len(broken_samples) > 0:
        broken_sample = broken_samples.sample(1).iloc[0]
        quiz = quiz_engine.generate_grammar_correction_quiz(broken_sample, broken_detector)
        if quiz:
            print(f"  질문: {quiz['question']}")
            print(f"  힌트: {quiz['hint']}")
            for i, choice in enumerate(quiz['choices']):
                mark = " <-- 정답" if i == quiz['correct_index'] else ""
                print(f"    {i+1}. {choice}{mark}")
            print(f"\n  설명:\n{quiz['explanation']}")
        else:
            print("  (비문법 없음)")
    else:
        print("  (비문법 표현 찾을 수 없음)")

    print("\n[OK] 테스트 완료!")
