"""Mr. Kim/Umma의 비문법 영어 감지 및 교정 모듈

intentional broken English 패턴을 학습 기회로 활용
"""

import json
import re
from pathlib import Path
from typing import Optional


class BrokenEnglishDetector:
    """비문법 영어 감지 및 교정 클래스"""

    def __init__(self, patterns_path: str | Path = "config/broken_patterns.json"):
        """
        Args:
            patterns_path: 비문법 패턴 JSON 파일 경로
        """
        self.patterns_path = Path(patterns_path)
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> list[dict]:
        """패턴 파일을 로드한다.

        Returns:
            패턴 리스트

        Raises:
            FileNotFoundError: 패턴 파일이 없을 때
        """
        if not self.patterns_path.exists():
            raise FileNotFoundError(f"패턴 파일을 찾을 수 없습니다: {self.patterns_path}")

        with open(self.patterns_path, encoding='utf-8') as f:
            data = json.load(f)
            return data.get("patterns", [])

    def detect_broken(self, text: str) -> list[dict]:
        """텍스트에서 비문법 패턴을 감지한다.

        Args:
            text: 검사할 텍스트

        Returns:
            감지된 패턴 리스트 [{"pattern_id": "...", "matched": "...", "correction": "...", ...}, ...]

        Example:
            >>> detector = BrokenEnglishDetector()
            >>> result = detector.detect_broken("You is very smart")
            >>> print(result[0]["pattern_id"])
            "BE_VERB_AGREEMENT_1"
        """
        detected = []

        for pattern_info in self.patterns:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                detected.append({
                    "pattern_id": pattern_info["id"],
                    "matched": match.group(0),
                    "correction": pattern_info["correction"],
                    "explanation": pattern_info["explanation"],
                    "start": match.start(),
                    "end": match.end(),
                    "example_wrong": pattern_info.get("example_wrong"),
                    "example_correct": pattern_info.get("example_correct")
                })

        # 위치 순서대로 정렬
        detected.sort(key=lambda x: x["start"])
        return detected

    def suggest_correction(self, text: str) -> dict[str, any]:
        """텍스트에 대한 교정 제안을 생성한다.

        Args:
            text: 원본 텍스트

        Returns:
            {"has_errors": bool, "original": str, "corrected": str, "issues": [...]}

        Example:
            >>> detector = BrokenEnglishDetector()
            >>> result = detector.suggest_correction("You is smart")
            >>> print(result["corrected"])
            "You are smart"
        """
        detected = self.detect_broken(text)

        if not detected:
            return {
                "has_errors": False,
                "original": text,
                "corrected": text,
                "issues": []
            }

        # 교정된 텍스트 생성 (뒤에서부터 교체해야 인덱스가 안 꼬임)
        corrected = text
        for issue in reversed(detected):
            corrected = (
                corrected[:issue["start"]] +
                issue["correction"] +
                corrected[issue["end"]:]
            )

        return {
            "has_errors": True,
            "original": text,
            "corrected": corrected,
            "issues": detected
        }

    def is_broken_english(self, text: str) -> bool:
        """텍스트에 비문법이 포함되어 있는지 확인한다.

        Args:
            text: 검사할 텍스트

        Returns:
            비문법이 포함되어 있으면 True

        Example:
            >>> detector = BrokenEnglishDetector()
            >>> detector.is_broken_english("You is smart")
            True
            >>> detector.is_broken_english("You are smart")
            False
        """
        return len(self.detect_broken(text)) > 0

    def get_grammar_point(self, pattern_id: str) -> Optional[dict]:
        """특정 패턴의 문법 포인트를 반환한다.

        Args:
            pattern_id: 패턴 ID (예: "BE_VERB_AGREEMENT_1")

        Returns:
            문법 포인트 정보, 없으면 None
        """
        for pattern in self.patterns:
            if pattern["id"] == pattern_id:
                return {
                    "id": pattern["id"],
                    "explanation": pattern["explanation"],
                    "example_wrong": pattern.get("example_wrong"),
                    "example_correct": pattern.get("example_correct")
                }
        return None

    def analyze_text(self, text: str, speaker: Optional[str] = None) -> dict:
        """텍스트를 분석하고 학습 자료를 생성한다.

        Args:
            text: 분석할 텍스트
            speaker: 화자 (Mr. Kim, Umma 등)

        Returns:
            분석 결과 딕셔너리

        Example:
            >>> detector = BrokenEnglishDetector()
            >>> result = detector.analyze_text("You is smart", "MR. KIM")
            >>> print(result["learning_note"])
            "Mr. Kim이 'You is'라고 말했지만, 올바른 표현은 'You are'입니다..."
        """
        correction = self.suggest_correction(text)

        if not correction["has_errors"]:
            return {
                "has_errors": False,
                "original": text,
                "speaker": speaker
            }

        # 학습 노트 생성
        learning_notes = []
        for issue in correction["issues"]:
            note = f"[X] '{issue['matched']}' → [OK] '{issue['correction']}'\n"
            note += f"[학습] {issue['explanation']}"

            if issue.get("example_wrong") and issue.get("example_correct"):
                note += f"\n   예) {issue['example_wrong']} → {issue['example_correct']}"

            learning_notes.append(note)

        speaker_note = ""
        if speaker and speaker.upper() in ["MR. KIM", "MR KIM", "UMMA"]:
            speaker_note = f"{speaker.title()}이 이렇게 말했지만, 올바른 표현은:\n"

        return {
            "has_errors": True,
            "original": correction["original"],
            "corrected": correction["corrected"],
            "speaker": speaker,
            "issues_count": len(correction["issues"]),
            "learning_notes": learning_notes,
            "learning_summary": speaker_note + f"'{correction['corrected']}'"
        }


def detect_broken(text: str, patterns_path: str = "config/broken_patterns.json") -> list[dict]:
    """텍스트에서 비문법 패턴을 감지한다. (편의 함수)

    Args:
        text: 검사할 텍스트
        patterns_path: 패턴 파일 경로

    Returns:
        감지된 패턴 리스트
    """
    detector = BrokenEnglishDetector(patterns_path)
    return detector.detect_broken(text)


def suggest_correction(text: str, patterns_path: str = "config/broken_patterns.json") -> dict:
    """텍스트에 대한 교정 제안을 생성한다. (편의 함수)

    Args:
        text: 원본 텍스트
        patterns_path: 패턴 파일 경로

    Returns:
        교정 제안 딕셔너리
    """
    detector = BrokenEnglishDetector(patterns_path)
    return detector.suggest_correction(text)


if __name__ == "__main__":
    # 테스트 코드
    print("=== 비문법 영어 감지 테스트 ===\n")

    detector = BrokenEnglishDetector("../config/broken_patterns.json")

    # 테스트 문장들
    test_cases = [
        ("You is very smart", "MR. KIM"),
        ("how I can help you?", "MR. KIM"),
        ("If you is the gay, it okay.", "MR. KIM"),
        ("They is all the gay", "MR. KIM"),
        ("I not understand", "UMMA"),
        ("He go to school", "UMMA"),
        ("You are very smart", "KEVIN"),  # 정상 문장
    ]

    for text, speaker in test_cases:
        print(f"화자: {speaker}")
        print(f"원문: {text}")

        result = detector.analyze_text(text, speaker)

        if result["has_errors"]:
            print(f"[OK] 교정: {result['corrected']}")
            print(f"[검색] 감지된 오류: {result['issues_count']}개")
            print("학습 노트:")
            for note in result["learning_notes"]:
                print(f"  {note}")
        else:
            print("[OK] 문법 오류 없음")

        print("-" * 60)
