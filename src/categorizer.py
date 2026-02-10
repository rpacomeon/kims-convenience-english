"""상황별 카테고리 분류 모듈

8개 카테고리: 인사/소개, 가게/쇼핑, 가족 대화, 감정 표현,
             부탁/거절, 직장/업무, 일상생활, 의견/조언
"""

import json
import re
from pathlib import Path
from typing import Optional

import pandas as pd


class Categorizer:
    """상황별 카테고리 분류 클래스"""

    def __init__(self, categories_path: str | Path = "config/categories.json"):
        """
        Args:
            categories_path: 카테고리 정의 JSON 파일 경로
        """
        self.categories_path = Path(categories_path)
        self.categories = self._load_categories()

    def _load_categories(self) -> list[dict]:
        """카테고리 파일을 로드한다.

        Returns:
            카테고리 리스트

        Raises:
            FileNotFoundError: 카테고리 파일이 없을 때
        """
        if not self.categories_path.exists():
            raise FileNotFoundError(f"카테고리 파일을 찾을 수 없습니다: {self.categories_path}")

        with open(self.categories_path, encoding='utf-8') as f:
            data = json.load(f)
            return data.get("categories", [])

    def categorize(self, text: str) -> list[str]:
        """텍스트를 카테고리로 분류한다.

        Args:
            text: 분류할 텍스트

        Returns:
            매칭된 카테고리 ID 리스트 (여러 카테고리에 속할 수 있음)

        Example:
            >>> categorizer = Categorizer()
            >>> categories = categorizer.categorize("Hello, how are you?")
            >>> print(categories)
            ["greetings"]
        """
        text_lower = text.lower()
        matched_categories = []

        for category in self.categories:
            category_id = category["id"]
            keywords = category.get("keywords", [])
            patterns = category.get("patterns", [])

            # 키워드 매칭
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched_categories.append(category_id)
                    break  # 이 카테고리는 이미 매칭됨

            # 패턴 매칭 (키워드로 매칭 안 된 경우만)
            if category_id not in matched_categories:
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        matched_categories.append(category_id)
                        break

        return matched_categories

    def get_primary_category(self, text: str) -> Optional[str]:
        """텍스트의 주 카테고리를 반환한다.

        Args:
            text: 분류할 텍스트

        Returns:
            주 카테고리 ID, 없으면 None

        Example:
            >>> categorizer = Categorizer()
            >>> category = categorizer.get_primary_category("Can you help me?")
            >>> print(category)
            "requests"
        """
        categories = self.categorize(text)
        return categories[0] if categories else None

    def get_category_name(self, category_id: str) -> Optional[str]:
        """카테고리 ID로 한글 이름을 가져온다.

        Args:
            category_id: 카테고리 ID

        Returns:
            한글 카테고리 이름, 없으면 None
        """
        for category in self.categories:
            if category["id"] == category_id:
                return category["name"]
        return None

    def get_all_categories(self) -> list[dict]:
        """모든 카테고리 정보를 반환한다.

        Returns:
            카테고리 리스트 [{"id": "...", "name": "..."}, ...]
        """
        return [
            {"id": cat["id"], "name": cat["name"]}
            for cat in self.categories
        ]

    def filter_by_category(
        self,
        df: pd.DataFrame,
        category_id: str
    ) -> pd.DataFrame:
        """특정 카테고리에 속하는 표현만 필터링한다.

        Args:
            df: 자막 DataFrame (clean_subtitle 컬럼 필요)
            category_id: 카테고리 ID

        Returns:
            필터링된 DataFrame (categories 컬럼 추가)

        Example:
            >>> categorizer = Categorizer()
            >>> df = load_subtitle_data("data.txt")
            >>> greetings = categorizer.filter_by_category(df, "greetings")
            >>> print(len(greetings))
        """
        df = df.copy()

        # categories 컬럼이 없으면 생성
        if 'categories' not in df.columns:
            df = add_category_column(df, self)

        # 특정 카테고리 포함 여부 확인
        def has_category(categories):
            if isinstance(categories, list):
                return category_id in categories
            return False

        df = df[df['categories'].apply(has_category)]
        return df.reset_index(drop=True)


def add_category_column(
    df: pd.DataFrame,
    categorizer: Optional[Categorizer] = None
) -> pd.DataFrame:
    """DataFrame에 카테고리 컬럼을 추가한다.

    Args:
        df: 자막 DataFrame (clean_subtitle 컬럼 필요)
        categorizer: Categorizer 인스턴스 (None이면 새로 생성)

    Returns:
        categories 컬럼이 추가된 DataFrame

    Example:
        >>> df = load_subtitle_data("data.txt")
        >>> df = add_category_column(df)
        >>> print(df['categories'].head())
    """
    if categorizer is None:
        categorizer = Categorizer()

    df = df.copy()

    # clean_subtitle 컬럼이 없으면 생성
    if 'clean_subtitle' not in df.columns:
        from data_loader import add_clean_subtitle_column
        df = add_clean_subtitle_column(df)

    df['categories'] = df['clean_subtitle'].apply(categorizer.categorize)
    df['primary_category'] = df['clean_subtitle'].apply(categorizer.get_primary_category)

    return df


def categorize(text: str, categories_path: str = "config/categories.json") -> list[str]:
    """텍스트를 카테고리로 분류한다. (편의 함수)

    Args:
        text: 분류할 텍스트
        categories_path: 카테고리 파일 경로

    Returns:
        매칭된 카테고리 ID 리스트
    """
    categorizer = Categorizer(categories_path)
    return categorizer.categorize(text)


if __name__ == "__main__":
    # 테스트 코드
    print("=== 카테고리 분류 테스트 ===\n")

    from data_loader import load_subtitle_data, add_clean_subtitle_column

    categorizer = Categorizer("../config/categories.json")

    # 1. 카테고리 목록
    print("[OK] 카테고리 목록:")
    for cat in categorizer.get_all_categories():
        print(f"  - {cat['id']}: {cat['name']}")

    # 2. 테스트 문장 분류
    test_sentences = [
        "Hello, nice to meet you!",
        "How much does this cost?",
        "I love you, mom.",
        "I'm so happy today!",
        "Can you help me with this?",
        "I have a meeting at the office.",
        "Let's have dinner together.",
        "I think you should try harder."
    ]

    print("\n[OK] 문장 분류 테스트:")
    for sentence in test_sentences:
        categories = categorizer.categorize(sentence)
        primary = categorizer.get_primary_category(sentence)
        cat_names = [categorizer.get_category_name(c) for c in categories]
        print(f"  \"{sentence}\"")
        print(f"    -> {', '.join(cat_names) or '분류 없음'} (주: {categorizer.get_category_name(primary) or 'N/A'})")

    # 3. 실제 데이터 분류
    print("\n[OK] 실제 데이터 분류:")
    df = load_subtitle_data("../김씨네 편의점.txt")
    df = add_clean_subtitle_column(df)
    df = add_category_column(df, categorizer)

    # 카테고리별 개수
    print(f"  전체 줄 수: {len(df)}")
    print(f"  분류된 줄 수: {len(df[df['primary_category'].notna()])}")

    # 카테고리별 분포
    category_counts = df['primary_category'].value_counts()
    print(f"\n  카테고리별 분포:")
    for cat_id, count in category_counts.head(8).items():
        cat_name = categorizer.get_category_name(cat_id)
        print(f"    {cat_name or cat_id}: {count}개")

    # 4. 특정 카테고리 필터링
    greetings = categorizer.filter_by_category(df, "greetings")
    print(f"\n[OK] 인사/소개 카테고리: {len(greetings)}개")
    print(f"  샘플:")
    for _, row in greetings.head(3).iterrows():
        print(f"    - {row['clean_subtitle'][:60]}")
