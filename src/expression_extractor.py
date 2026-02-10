"""핵심 표현 필터링 및 추출 모듈

유용한 학습 표현을 선별하고 난이도를 태깅
"""

import re
from typing import Optional

import pandas as pd


def filter_useful_lines(df: pd.DataFrame) -> pd.DataFrame:
    """유용한 학습 라인만 필터링한다.

    Args:
        df: 자막 DataFrame

    Returns:
        필터링된 DataFrame

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> useful = filter_useful_lines(df)
        >>> print(len(useful), "lines")
    """
    df = df.copy()

    # clean_subtitle 컬럼이 없으면 생성
    if 'clean_subtitle' not in df.columns:
        from data_loader import add_clean_subtitle_column
        df = add_clean_subtitle_column(df)

    # 제외 조건
    # 1. 빈 문자열
    df = df[df['clean_subtitle'].str.strip() != '']

    # 2. 너무 짧은 문장 (1~2단어) - 단, 유용한 단문은 예외
    useful_short = ['yes', 'no', 'okay', 'sure', 'thanks', 'sorry', 'please',
                    'hello', 'hi', 'bye', 'welcome', 'excuse me']

    def is_useful_or_long(text: str) -> bool:
        """유용한 표현이거나 3단어 이상인지 확인"""
        text_lower = text.lower().strip()

        # 유용한 단문인 경우
        for short in useful_short:
            if text_lower == short or text_lower.startswith(short + ','):
                return True

        # 3단어 이상인 경우
        words = text.split()
        return len(words) >= 3

    df = df[df['clean_subtitle'].apply(is_useful_or_long)]

    # 3. 무대지시어만 있는 경우 (여전히 남아있을 수 있음)
    df = df[~df['clean_subtitle'].str.match(r'^\([A-Z\s,]+\)$')]

    return df.reset_index(drop=True)


def calculate_sentence_quality(text: str) -> float:
    """문장의 학습 품질 점수를 계산한다.

    Args:
        text: 문장 텍스트

    Returns:
        품질 점수 (0.0 ~ 1.0)

    품질 기준:
    - 적절한 길이 (5~20단어): +0.3
    - 완전한 문장 (주어+동사): +0.2
    - 일상 표현 포함: +0.2
    - 구동사 포함: +0.2
    - 의문문/명령문: +0.1
    """
    score = 0.0
    words = text.split()
    word_count = len(words)

    # 1. 적절한 길이
    if 5 <= word_count <= 20:
        score += 0.3
    elif 3 <= word_count <= 25:
        score += 0.15

    # 2. 완전한 문장 (주어+동사 패턴)
    has_subject_verb = bool(re.search(r'\b(I|you|he|she|it|we|they|this|that)\s+\w+', text, re.I))
    if has_subject_verb:
        score += 0.2

    # 3. 일상 표현 포함
    common_phrases = [
        'how are you', 'nice to meet', 'thank you', 'excuse me',
        'I think', 'you know', 'I mean', 'by the way', 'come on',
        'hold on', 'wait a minute', 'let me', 'can I', 'could you'
    ]
    text_lower = text.lower()
    if any(phrase in text_lower for phrase in common_phrases):
        score += 0.2

    # 4. 구동사 포함 (동사 + 전치사/부사)
    phrasal_verb_pattern = r'\b(get|go|come|take|put|look|turn|give|make|break|run|pick|set|bring|call|find|work|hang|catch)\s+(up|down|in|out|on|off|over|away|back|through|along|after|into|for)\b'
    if re.search(phrasal_verb_pattern, text, re.I):
        score += 0.2

    # 5. 의문문/명령문
    if text.strip().endswith('?'):
        score += 0.1
    elif re.match(r'^(please|let\'s|don\'t|do|can|could|would)\s', text, re.I):
        score += 0.1

    return min(score, 1.0)


def extract_key_expressions(
    df: pd.DataFrame,
    episode: Optional[int] = None,
    top_n: int = 25
) -> pd.DataFrame:
    """에피소드별 핵심 표현을 추출한다.

    Args:
        df: 자막 DataFrame
        episode: 에피소드 번호 (None이면 전체)
        top_n: 상위 N개 표현

    Returns:
        핵심 표현 DataFrame (quality_score 컬럼 포함)

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> key_expr = extract_key_expressions(df, episode=1, top_n=25)
        >>> print(key_expr.head())
    """
    # 에피소드 필터링
    if episode is not None:
        if 'episode' not in df.columns:
            from data_loader import add_episode_column
            df = add_episode_column(df)
        df = df[df['episode'] == episode].copy()

    # 유용한 라인만 필터링
    df = filter_useful_lines(df)

    # 품질 점수 계산
    df['quality_score'] = df['clean_subtitle'].apply(calculate_sentence_quality)

    # 상위 N개 선택 (품질 점수 + 다양성)
    # 1차: 품질 점수 상위 top_n * 2
    top_candidates = df.nlargest(top_n * 2, 'quality_score')

    # 2차: 다양성 확보 (유사한 문장 제거)
    selected = []
    selected_texts = []

    for _, row in top_candidates.iterrows():
        text = row['clean_subtitle'].lower()

        # 이미 선택된 문장과 너무 유사하면 제외
        is_similar = False
        for selected_text in selected_texts:
            # 간단한 유사도: 공통 단어 비율
            words1 = set(text.split())
            words2 = set(selected_text.split())
            if len(words1) == 0 or len(words2) == 0:
                continue
            similarity = len(words1 & words2) / max(len(words1), len(words2))
            if similarity > 0.7:  # 70% 이상 유사
                is_similar = True
                break

        if not is_similar:
            selected.append(row)
            selected_texts.append(text)

        if len(selected) >= top_n:
            break

    result_df = pd.DataFrame(selected)
    return result_df.reset_index(drop=True)


def tag_difficulty(text: str) -> str:
    """문장의 난이도를 태깅한다.

    Args:
        text: 문장 텍스트

    Returns:
        "beginner", "intermediate", "advanced"

    난이도 기준:
    - beginner: 기초 단어, 현재 시제, 단순 구조
    - intermediate: 과거/미래 시제, 접속사, 관계대명사
    - advanced: 복잡한 구조, 고급 어휘, 가정법
    """
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)

    # Advanced 패턴
    advanced_patterns = [
        r'\b(would have|could have|should have)\b',  # 가정법 과거
        r'\b(had \w+ed|had been)\b',  # 과거완료
        r'\b(although|whereas|nevertheless|furthermore)\b',  # 고급 접속사
        r'\b(whom|whose)\b',  # 관계대명사 격
    ]
    if any(re.search(pattern, text_lower) for pattern in advanced_patterns):
        return "advanced"

    # Intermediate 패턴
    intermediate_patterns = [
        r'\b(will|would|could|should|might)\b',  # 조동사
        r'\b(\w+ed|went|came|saw)\b',  # 과거 시제
        r'\b(because|although|unless|since|while)\b',  # 접속사
        r'\b(which|that|who)\b.*\b(is|are|was|were)\b',  # 관계대명사절
        r'\b(have been|has been)\b',  # 현재완료
    ]
    if any(re.search(pattern, text_lower) for pattern in intermediate_patterns):
        return "intermediate"

    # 문장 길이로도 판단
    if word_count > 15:
        return "intermediate"
    elif word_count > 20:
        return "advanced"

    # 기본값: beginner
    return "beginner"


def add_difficulty_column(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame에 난이도 컬럼을 추가한다.

    Args:
        df: 자막 DataFrame

    Returns:
        difficulty 컬럼이 추가된 DataFrame
    """
    df = df.copy()
    df['difficulty'] = df['clean_subtitle'].apply(tag_difficulty)
    return df


if __name__ == "__main__":
    # 테스트 코드
    print("=== 표현 추출 테스트 ===\n")

    from data_loader import load_subtitle_data, add_episode_column, add_clean_subtitle_column

    # 데이터 로드
    df = load_subtitle_data("../김씨네 편의점.txt")
    df = add_episode_column(df)
    df = add_clean_subtitle_column(df)

    # 1. 유용한 라인 필터링
    useful = filter_useful_lines(df)
    print(f"[OK] 유용한 라인: {len(useful)}줄 (전체 {len(df)}줄 중)")

    # 2. Episode 1 핵심 표현 추출
    key_ep1 = extract_key_expressions(df, episode=1, top_n=10)
    print(f"\n[OK] Episode 1 핵심 표현 상위 10개:")
    for i, row in key_ep1.iterrows():
        print(f"  {i+1}. [{row.get('quality_score', 0):.2f}] {row['clean_subtitle'][:60]}")

    # 3. 난이도 태깅
    key_ep1 = add_difficulty_column(key_ep1)
    print(f"\n[OK] 난이도 분포:")
    print(key_ep1['difficulty'].value_counts().to_dict())

    # 4. 전체 에피소드에서 high-quality 표현
    all_useful = filter_useful_lines(df)
    all_useful['quality_score'] = all_useful['clean_subtitle'].apply(calculate_sentence_quality)
    top_overall = all_useful.nlargest(20, 'quality_score')
    print(f"\n[OK] 전체 최고 품질 표현 상위 5개:")
    for i, row in top_overall.head(5).iterrows():
        print(f"  {i+1}. [Ep.{row.get('episode', '?')}] [{row['quality_score']:.2f}] {row['clean_subtitle'][:60]}")
