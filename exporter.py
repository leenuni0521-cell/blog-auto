"""
exporter.py
생성된 블로그 글을 로컬 파일로 저장하는 모듈

drafts/
└── 미주이야기/
    ├── [01.15] S&P500이 뭔지 몰랐던 내가 투자를 시작한 이유.txt
    └── [01.17] 미국 주식, 환율이 무서웠던 나의 첫 매수 이야기.txt
└── AI이야기/
└── 투자일기/
"""

import os
from datetime import datetime


def export_to_local(post_data):
    series_name = post_data.get("series_name", post_data.get("series_id", "기타"))
    title = post_data["title"]
    content = post_data["content"]

    # 시리즈별 폴더 생성
    folder_path = os.path.join("drafts", series_name.replace("/", "-").strip())
    os.makedirs(folder_path, exist_ok=True)

    # 파일 이름: [날짜] 제목.txt
    today = datetime.now().strftime("%m.%d")
    safe_title = title[:40].replace("/", "-").replace("?", "").replace(":", "")
    filename = f"[{today}] {safe_title}.txt"
    filepath = os.path.join(folder_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"제목: {title}\n")
        f.write(f"시리즈: {series_name}\n")
        f.write(f"작성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)

    print(f"✅ 저장 완료!")
    print(f"📂 위치: {os.path.abspath(filepath)}")

    return {
        "success": True,
        "filepath": filepath,
        "abspath": os.path.abspath(filepath)
    }


if __name__ == "__main__":
    test_post = {
        "title": "배당주 투자 완벽 가이드",
        "content": "테스트 내용이에요!\n\n💰 배당주란?\n\n이런 식으로 글이 들어갑니다.",
        "series_id": "미주이야기",
        "series_name": "📈 미주이야기"
    }
    result = export_to_local(test_post)
    print(result)
