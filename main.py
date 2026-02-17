"""
main.py
블로그 자동화 메인 컨트롤러 + 스케줄러
글 생성 후 Google Docs로 자동 내보내기
"""

import json
import schedule
import time
import argparse
from datetime import datetime
from writer import generate_post, get_next_topic, mark_topic_done
from exporter import export_to_local


def run_auto_post(series_id=None, dry_run=False):
    """
    글 생성 → 포스팅 전체 흐름을 실행합니다.
    
    series_id: 특정 시리즈 지정 (None이면 자동 선택)
    dry_run: True면 글 생성만 하고 실제 포스팅은 안 함 (테스트용)
    """
    print("\n" + "="*50)
    print(f"🚀 블로그 자동화 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    # 1. 다음 주제 가져오기
    topic = get_next_topic(series_id)
    
    if not topic:
        print("❌ 남은 주제가 없습니다. series.json을 업데이트해주세요!")
        return
    
    print(f"\n📌 선택된 주제: [{topic['series_name']}] {topic['title']}")
    
    # 2. Claude API로 글 생성
    post_result = generate_post(topic)
    
    if dry_run:
        print(f"\n🧪 DRY RUN - drafts 폴더에만 저장됨: {post_result['filepath']}")
        print("\n--- 미리보기 ---")
        print(post_result["content"][:600])
        print("...")
        return
    
    # 3. Google Docs로 내보내기
    export_result = export_to_local({
        "title": post_result["title"],
        "content": post_result["content"],
        "series_id": topic["series_id"],
        "series_name": topic["series_name"]
    })
    
    if export_result["success"]:
        # 4. 완료 처리
        mark_topic_done(topic["series_id"], topic["title"])
        print(f"\n🎉 완료! 아래 경로에서 파일 열어보고 네이버에 복붙하세요 😊")
        print(f"📂 {export_result["abspath"]}")
    else:
        print(f"\n❌ 내보내기 실패. drafts/{post_result['filepath']} 에서 확인하세요.")


def auto_schedule():
    """스케줄러를 실행합니다 (config.json의 설정 기반)."""
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    sched_config = config.get("schedule", {})
    if not sched_config.get("enabled", False):
        print("⚠️  스케줄 기능이 비활성화되어 있습니다.")
        return
    
    post_time = sched_config.get("time", "09:00")
    days = sched_config.get("days", ["mon", "wed", "fri"])
    
    day_map = {
        "mon": schedule.every().monday,
        "tue": schedule.every().tuesday,
        "wed": schedule.every().wednesday,
        "thu": schedule.every().thursday,
        "fri": schedule.every().friday,
        "sat": schedule.every().saturday,
        "sun": schedule.every().sunday,
    }
    
    for day in days:
        if day in day_map:
            day_map[day].at(post_time).do(run_auto_post, dry_run=False)
    
    print(f"⏰ 스케줄러 시작! 매주 {', '.join(days)} {post_time}에 자동 포스팅됩니다.")
    print("   종료하려면 Ctrl+C를 누르세요.\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def show_status():
    """시리즈별 진행 상황을 보여줍니다."""
    with open("series.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("\n📊 시리즈별 진행 현황")
    print("="*50)
    
    for series in data["series"]:
        total = len(series["topics"])
        done = sum(1 for t in series["topics"] if t["done"])
        remaining = total - done
        
        bar = "█" * done + "░" * remaining
        print(f"\n{series['name']}")
        print(f"  진행: [{bar}] {done}/{total}")
        
        # 다음 주제 표시
        next_topics = [t for t in series["topics"] if not t["done"]]
        if next_topics:
            print(f"  📌 다음: {next_topics[0]['title']}")
        else:
            print(f"  ✅ 완료!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="네이버 블로그 자동화")
    parser.add_argument("command", nargs="?", default="run",
                       choices=["run", "schedule", "status", "test"],
                       help="실행 모드")
    parser.add_argument("--series", "-s", type=str, 
                       help="시리즈 ID (미주이야기/AI이야기/투자일기)")
    
    args = parser.parse_args()
    
    if args.command == "run":
        # 글 생성 + 포스팅 실행
        run_auto_post(series_id=args.series, dry_run=False)
    
    elif args.command == "test":
        # 글 생성만 (포스팅 X)
        run_auto_post(series_id=args.series, dry_run=True)
    
    elif args.command == "schedule":
        # 자동 스케줄 모드
        auto_schedule()
    
    elif args.command == "status":
        # 진행 현황 보기
        show_status()
