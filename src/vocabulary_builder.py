"""단어 추출 및 빈도 분석 모듈

드라마 속 실제 예문과 함께 어휘력 학습 지원
"""

import re
from collections import Counter
from typing import Optional

import pandas as pd


# 불용어 (학습 가치가 낮은 단어)
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'should', 'could', 'may', 'might', 'must',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
    'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
    'this', 'that', 'these', 'those', 'am', 'been', 'can'
}

# 고유명사 (드라마 캐릭터 등)
PROPER_NOUNS = {
    'kevin', 'janet', 'jung', 'kimchee', 'appa', 'umma', 'shannon',
    'gerald', 'semira', 'chelsea', 'enrico', 'roger', 'nayoung',
    'mr', 'mrs', 'ms', 'miss', 'dr', 'kim', 'terence'
}


def clean_word(word: str) -> str:
    """단어를 정제한다.

    Args:
        word: 원본 단어

    Returns:
        정제된 단어 (소문자, 특수문자 제거)

    Example:
        >>> clean_word("Hello,")
        "hello"
        >>> clean_word("don't")
        "don't"
    """
    # 단어 양쪽의 구두점 제거 (단, 축약형의 ' 는 유지)
    word = re.sub(r'^[^\w\']+|[^\w\']+$', '', word)
    return word.lower()


def is_valid_word(word: str) -> bool:
    """학습 가치가 있는 단어인지 확인한다.

    Args:
        word: 검사할 단어

    Returns:
        유효한 단어이면 True

    조건:
    - 2글자 이상
    - 불용어가 아님
    - 고유명사가 아님
    - 숫자가 아님
    """
    if len(word) < 2:
        return False

    if word.lower() in STOPWORDS:
        return False

    if word.lower() in PROPER_NOUNS:
        return False

    if word.isdigit():
        return False

    return True


def extract_words(text: str) -> list[str]:
    """텍스트에서 유효한 단어를 추출한다.

    Args:
        text: 원본 텍스트

    Returns:
        정제된 단어 리스트

    Example:
        >>> extract_words("Hello, world! How are you?")
        ["hello", "world"]
    """
    # 단어 분리 (축약형 유지)
    words = re.findall(r"\b[\w']+\b", text)

    # 정제 및 필터링
    cleaned = [clean_word(w) for w in words]
    valid = [w for w in cleaned if is_valid_word(w)]

    return valid


def extract_vocabulary(
    df: pd.DataFrame,
    episode: Optional[int] = None,
    min_freq: int = 2
) -> pd.DataFrame:
    """에피소드에서 어휘를 추출하고 빈도 분석한다.

    Args:
        df: 자막 DataFrame
        episode: 에피소드 번호 (None이면 전체)
        min_freq: 최소 출현 빈도

    Returns:
        어휘 DataFrame (word, frequency 컬럼)

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> vocab = extract_vocabulary(df, episode=1, min_freq=3)
        >>> print(vocab.head())
    """
    # 에피소드 필터링
    if episode is not None:
        if 'episode' not in df.columns:
            from data_loader import add_episode_column
            df = add_episode_column(df)
        df = df[df['episode'] == episode].copy()

    # clean_subtitle 컬럼이 없으면 생성
    if 'clean_subtitle' not in df.columns:
        from data_loader import add_clean_subtitle_column
        df = add_clean_subtitle_column(df)

    # 모든 단어 추출
    all_words = []
    for text in df['clean_subtitle']:
        words = extract_words(text)
        all_words.extend(words)

    # 빈도 계산
    word_counts = Counter(all_words)

    # 최소 빈도 필터링
    filtered = {word: count for word, count in word_counts.items() if count >= min_freq}

    # DataFrame으로 변환
    vocab_df = pd.DataFrame([
        {"word": word, "frequency": count}
        for word, count in filtered.items()
    ])

    # 빈도순 정렬
    vocab_df = vocab_df.sort_values('frequency', ascending=False).reset_index(drop=True)

    return vocab_df


def get_word_examples(
    df: pd.DataFrame,
    word: str,
    max_examples: int = 3
) -> list[dict]:
    """특정 단어의 실제 사용 예문을 가져온다.

    Args:
        df: 자막 DataFrame
        word: 검색할 단어
        max_examples: 최대 예문 개수

    Returns:
        예문 리스트 [{"english": "...", "korean": "...", "episode": 1}, ...]

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> examples = get_word_examples(df, "happy", max=3)
        >>> for ex in examples:
        >>>     print(ex["english"])
    """
    # clean_subtitle 컬럼이 없으면 생성
    if 'clean_subtitle' not in df.columns:
        from data_loader import add_clean_subtitle_column
        df = add_clean_subtitle_column(df)

    # episode 컬럼이 없으면 생성
    if 'episode' not in df.columns:
        from data_loader import add_episode_column
        df = add_episode_column(df)

    # 단어가 포함된 문장 찾기 (단어 경계 고려)
    pattern = rf'\b{re.escape(word)}\b'
    matching_rows = df[df['clean_subtitle'].str.contains(pattern, case=False, regex=True)]

    # 최대 개수만큼 샘플링
    samples = matching_rows.sample(min(max_examples, len(matching_rows)))

    examples = []
    for _, row in samples.iterrows():
        examples.append({
            "english": row['clean_subtitle'],
            "korean": row.get('Machine Translation', ''),
            "episode": row.get('episode', None)
        })

    return examples


def analyze_phrasal_verbs(df: pd.DataFrame, phrasal_verbs_path: str = "config/phrasal_verbs.json") -> pd.DataFrame:
    """드라마에서 구동사 사용 빈도를 분석한다.

    Args:
        df: 자막 DataFrame
        phrasal_verbs_path: 구동사 정의 파일 경로

    Returns:
        구동사 빈도 DataFrame (verb, meaning, frequency, examples 컬럼)

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> phrasal_analysis = analyze_phrasal_verbs(df)
        >>> print(phrasal_analysis.head())
    """
    import json
    from pathlib import Path

    # 구동사 로드
    with open(Path(phrasal_verbs_path), encoding='utf-8') as f:
        data = json.load(f)
        phrasal_verbs = data.get("phrasal_verbs", [])

    # clean_subtitle 컬럼이 없으면 생성
    if 'clean_subtitle' not in df.columns:
        from data_loader import add_clean_subtitle_column
        df = add_clean_subtitle_column(df)

    results = []

    for pv in phrasal_verbs:
        verb = pv["verb"]
        meaning = pv["meaning"]

        # 구동사 패턴 매칭 (단어 경계 고려)
        # 예: "come in" → "\bcome\s+in\b"
        pattern = r'\b' + re.escape(verb.replace(' ', r'\s+')) + r'\b'

        matching_rows = df[df['clean_subtitle'].str.contains(pattern, case=False, regex=True)]
        frequency = len(matching_rows)

        if frequency > 0:
            # 예문 최대 3개
            examples = []
            for _, row in matching_rows.head(3).iterrows():
                examples.append({
                    "english": row['clean_subtitle'],
                    "korean": row.get('Machine Translation', '')
                })

            results.append({
                "verb": verb,
                "meaning": meaning,
                "category": pv.get("category", ""),
                "frequency": frequency,
                "examples": examples
            })

    # DataFrame으로 변환 및 정렬
    result_df = pd.DataFrame(results)
    if len(result_df) > 0:
        result_df = result_df.sort_values('frequency', ascending=False).reset_index(drop=True)

    return result_df


if __name__ == "__main__":
    # 테스트 코드
    print("=== 어휘 추출 테스트 ===\n")

    from data_loader import load_subtitle_data, add_episode_column, add_clean_subtitle_column

    # 데이터 로드
    df = load_subtitle_data("../김씨네 편의점.txt")
    df = add_episode_column(df)
    df = add_clean_subtitle_column(df)

    # 1. Episode 1 어휘 추출
    vocab_ep1 = extract_vocabulary(df, episode=1, min_freq=3)
    print(f"[OK] Episode 1 어휘 (3회 이상): {len(vocab_ep1)}개")
    print(f"  상위 10개:")
    for i, row in vocab_ep1.head(10).iterrows():
        print(f"    {i+1}. {row['word']}: {row['frequency']}회")

    # 2. 단어 예문 가져오기
    word = "happy"
    examples = get_word_examples(df, word, max_examples=3)
    print(f"\n[OK] '{word}' 사용 예문 ({len(examples)}개):")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. [Ep.{ex['episode']}] {ex['english']}")
        print(f"     ({ex['korean']})")

    # 3. 구동사 분석
    phrasal_analysis = analyze_phrasal_verbs(df, "../config/phrasal_verbs.json")
    print(f"\n[OK] 구동사 분석: 드라마에서 사용된 구동사 {len(phrasal_analysis)}개")
    print(f"  상위 10개:")
    for i, row in phrasal_analysis.head(10).iterrows():
        print(f"    {i+1}. {row['verb']} ({row['meaning']}): {row['frequency']}회")

    # 4. 전체 어휘 통계
    vocab_all = extract_vocabulary(df, episode=None, min_freq=5)
    print(f"\n[OK] 전체 어휘 (5회 이상): {len(vocab_all)}개")
    print(f"  가장 빈도 높은 5개:")
    for i, row in vocab_all.head(5).iterrows():
        print(f"    {i+1}. {row['word']}: {row['frequency']}회")
