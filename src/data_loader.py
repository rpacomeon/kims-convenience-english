"""김씨네 편의점 자막 데이터 로더

TSV 파일 파싱, 화자 식별, 에피소드 그룹핑 기능 제공
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd


def load_subtitle_data(path: str | Path) -> pd.DataFrame:
    """자막 데이터를 로드한다.

    Args:
        path: 자막 파일 경로 (TSV 형식)

    Returns:
        자막 DataFrame (columns: 파일이름, Subtitle, Machine Translation, Time, 분, 초)

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
        ValueError: 파일을 읽을 수 없을 때 (인코딩 오류)

    Example:
        >>> df = load_subtitle_data("김씨네 편의점.txt")
        >>> print(len(df))
        5694
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    # AP-004: 한글 인코딩 fallback
    encodings = ['utf-8', 'cp949', 'euc-kr']

    for encoding in encodings:
        try:
            # 첫 줄을 헤더로 읽기
            # on_bad_lines='skip': 파싱 오류 줄은 건너뛰기 (로그는 출력)
            df = pd.read_csv(
                path,
                sep='\t',
                encoding=encoding,
                header=0,
                on_bad_lines='warn',  # 경고만 출력하고 계속 진행
                engine='python',  # 파이썬 엔진은 더 유연함
                quoting=3  # QUOTE_NONE: 인용 부호를 특수하게 처리하지 않음
            )

            return df

        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise ValueError(f"파일 읽기 실패 ({encoding}): {e}")

    raise ValueError(f"모든 인코딩 시도 실패: {encodings}")


def parse_episode_number(filename: str) -> Optional[int]:
    """파일명에서 에피소드 번호를 추출한다.

    Args:
        filename: 파일명 (예: "김씨네편의점_season01_03.xlsx")

    Returns:
        에피소드 번호 (1~13), 없으면 None

    Example:
        >>> parse_episode_number("김씨네편의점_season01_03.xlsx")
        3
        >>> parse_episode_number("김씨네편의점_season01_10.xlsx")
        10
    """
    # 패턴: season01_XX 또는 season01_X
    pattern = r'season\d+_(\d+)'
    match = re.search(pattern, filename)

    if match:
        return int(match.group(1))

    return None


def identify_speaker(subtitle: str) -> Optional[str]:
    """자막에서 화자를 식별한다.

    Args:
        subtitle: 자막 텍스트 (예: "-KEVIN: Hello, Mr. Kim.")

    Returns:
        화자 이름 (대문자), 없으면 None

    Example:
        >>> identify_speaker("-KEVIN: Hello, Mr. Kim.")
        "KEVIN"
        >>> identify_speaker("-Mr. Kim: Good morning.")
        "MR. KIM"
        >>> identify_speaker("Hello there")
        None
    """
    # 패턴: -화자이름: 으로 시작
    pattern = r'^-([A-Za-z\s\.]+?):\s*'
    match = re.match(pattern, subtitle)

    if match:
        speaker = match.group(1).strip().upper()
        return speaker

    return None


def split_multi_speaker(subtitle: str) -> list[dict[str, str]]:
    """여러 화자가 포함된 자막을 분리한다.

    Args:
        subtitle: 자막 텍스트 (예: "-KEVIN: Hi. -Roger: Hey.")

    Returns:
        화자별 대사 리스트 [{"speaker": "KEVIN", "text": "Hi."}, ...]

    Example:
        >>> split_multi_speaker("-KEVIN: Hello. -Roger: Hi there.")
        [{"speaker": "KEVIN", "text": "Hello."}, {"speaker": "ROGER", "text": "Hi there."}]
    """
    # 패턴: -화자: 대사 형태를 찾아 분리
    pattern = r'-([A-Za-z\s\.]+?):\s*([^-]+?)(?=\s*-[A-Za-z]|$)'
    matches = re.findall(pattern, subtitle)

    result = []
    for speaker, text in matches:
        result.append({
            "speaker": speaker.strip().upper(),
            "text": text.strip()
        })

    return result if result else [{"speaker": None, "text": subtitle.strip()}]


def clean_subtitle(text: str) -> str:
    """자막에서 무대지시어와 화자 태그를 제거한다.

    Args:
        text: 원본 자막 텍스트

    Returns:
        정제된 텍스트

    Example:
        >>> clean_subtitle("-KEVIN: (LAUGHS) That's funny!")
        "That's funny!"
        >>> clean_subtitle("(DOOR OPENS) Hello there.")
        "Hello there."
    """
    # 무대지시어 제거 (괄호 안의 대문자 텍스트)
    text = re.sub(r'\([A-Z\s,]+\)', '', text)

    # 화자 태그 제거
    text = re.sub(r'^-[A-Za-z\s\.]+:\s*', '', text)

    # 연속된 공백 정리
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def add_episode_column(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame에 에피소드 번호 컬럼을 추가한다.

    Args:
        df: 자막 DataFrame

    Returns:
        episode 컬럼이 추가된 DataFrame

    Example:
        >>> df = load_subtitle_data("김씨네 편의점.txt")
        >>> df = add_episode_column(df)
        >>> print(df['episode'].unique())
        [1, 2, 3, ..., 13]
    """
    df = df.copy()
    df['episode'] = df['파일이름'].apply(parse_episode_number)
    return df


def add_speaker_column(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame에 화자 컬럼을 추가한다.

    Args:
        df: 자막 DataFrame

    Returns:
        speaker 컬럼이 추가된 DataFrame

    Example:
        >>> df = load_subtitle_data("김씨네 편의점.txt")
        >>> df = add_speaker_column(df)
        >>> print(df['speaker'].value_counts())
    """
    df = df.copy()
    df['speaker'] = df['Subtitle'].apply(identify_speaker)
    return df


def add_clean_subtitle_column(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame에 정제된 자막 컬럼을 추가한다.

    Args:
        df: 자막 DataFrame

    Returns:
        clean_subtitle 컬럼이 추가된 DataFrame
    """
    df = df.copy()
    df['clean_subtitle'] = df['Subtitle'].apply(clean_subtitle)
    return df


if __name__ == "__main__":
    # 테스트 코드
    print("=== 데이터 로더 테스트 ===")

    # 1. 데이터 로드
    df = load_subtitle_data("../김씨네 편의점.txt")
    print(f"[OK] 데이터 로드 완료: {len(df)}줄")

    # 2. 에피소드 추가
    df = add_episode_column(df)
    print(f"[OK] 에피소드 범위: {df['episode'].min()} ~ {df['episode'].max()}")

    # 3. 화자 식별
    df = add_speaker_column(df)
    print(f"[OK] 화자 수: {df['speaker'].nunique()}명")
    print(f"  주요 화자: {df['speaker'].value_counts().head(5).to_dict()}")

    # 4. 자막 정제
    df = add_clean_subtitle_column(df)
    print(f"[OK] 자막 정제 완료")

    # 5. 샘플 출력
    print("\n=== 샘플 데이터 (Episode 1, 처음 5줄) ===")
    sample = df[df['episode'] == 1].head(5)
    for _, row in sample.iterrows():
        print(f"[{row['speaker'] or 'UNKNOWN'}] {row['clean_subtitle']}")
