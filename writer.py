"""
writer.py
Claude API를 활용해 블로그 글을 자동 생성하는 모듈
"""

import anthropic
import json
import os

# 블로그 스타일 시스템 프롬프트
STYLE_PROMPT = """
당신은 경제/AI 블로그를 운영하는 블로거입니다.
아래 스타일 가이드를 정확하게 따라 블로그 글을 작성해주세요.

## 말투 & 톤
- 친근한 해요체 사용 (~해요, ~이에요, ~더라구요, ~했는데, ~거든요)
- 딱딱하지 않고 대화하듯 자연스럽게
- 솔직하고 개인적인 경험을 녹여서 ("저는 처음에 이게 뭔지도 몰랐어요", "솔직히 말하면")
- 초보자 눈높이 설명 (어려운 용어는 반드시 쉽게 풀어쓰기)

## 글 구조
1. **도입부**: 개인 경험이나 공감되는 상황으로 시작
2. **본문**: 이모지가 붙은 소제목으로 섹션 구분
3. **마무리**: 요약 + 다음 편 예고 또는 독자에게 한마디

## 형식 규칙
- 소제목 앞에 이모지 필수 (💰, 📈, 🎯, ⚠️, 💡, 🏆 등 내용에 맞게)
- 이미지 자리는 아래 형식으로 표시:
  [이미지: (이미지 설명)]
- 중요한 수치나 정보는 별도 줄로 강조
- 리스트 활용 (✅, 👉 등 기호 사용)
- 글 끝에 반드시 해시태그 추가

## 길이
- 미주이야기/AI이야기: 1,500~2,500자 (이미지 자리 포함)
- 투자일기: 800~1,500자

## 예시 문장 패턴
- "~인 줄 몰랐어요" / "~해봤는데 솔직히"
- "초보였던 저도 이해했으니까 여러분도 분명 되실 거예요!"
- "다음 편에서는 ~에 대해 다뤄볼 예정이에요!"
"""

def get_next_topic(series_id=None):
    """series.json에서 다음에 쓸 주제를 가져옵니다."""
    with open("series.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # series_id가 지정되면 해당 시리즈, 없으면 자동 선택
    for series in data["series"]:
        if series_id and series["id"] != series_id:
            continue
        for topic in series["topics"]:
            if not topic["done"]:
                return {
                    "series_name": series["name"],
                    "series_id": series["id"],
                    "title": topic["title"],
                    "hashtags": series["hashtags"],
                    "description": series["description"]
                }
    return None


def mark_topic_done(series_id, title):
    """완료된 주제를 done=true로 업데이트합니다."""
    with open("series.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for series in data["series"]:
        if series["id"] == series_id:
            for topic in series["topics"]:
                if topic["title"] == title:
                    topic["done"] = True
                    break
    
    with open("series.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 완료 처리: [{series_id}] {title}")


def generate_post(topic_info, custom_notes=""):
    """Claude API로 블로그 글을 생성합니다."""
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    client = anthropic.Anthropic(api_key=config["anthropic"]["api_key"])
    
    user_prompt = f"""
시리즈: {topic_info['series_name']}
시리즈 설명: {topic_info['description']}
이번 글 제목: {topic_info['title']}
해시태그: {topic_info['hashtags']}
{f"추가 메모: {custom_notes}" if custom_notes else ""}

위 정보를 바탕으로 네이버 블로그에 올릴 글을 작성해주세요.
글 맨 아래에 해시태그를 포함해주세요.
"""
    
    print(f"✍️  글 생성 중: {topic_info['title']}")
    
    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=4096,
        system=STYLE_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    content = message.content[0].text
    print(f"✅ 글 생성 완료! ({len(content)}자)")
    
    # 생성된 글 저장
    os.makedirs("drafts", exist_ok=True)
    safe_title = topic_info['title'][:30].replace("/", "-").replace(" ", "_")
    filepath = f"drafts/{topic_info['series_id']}_{safe_title}.txt"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"제목: {topic_info['title']}\n")
        f.write(f"시리즈: {topic_info['series_name']}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)
    
    print(f"💾 초안 저장: {filepath}")
    
    return {
        "title": topic_info["title"],
        "content": content,
        "series_id": topic_info["series_id"],
        "filepath": filepath
    }


if __name__ == "__main__":
    # 테스트 실행
    topic = get_next_topic()
    if topic:
        result = generate_post(topic)
        print("\n" + "="*50)
        print("📄 생성된 글 미리보기 (앞 500자):")
        print(result["content"][:500])
    else:
        print("❌ 남은 주제가 없습니다.")
