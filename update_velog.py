import feedparser
import os

# Velog RSS 피드 주소 (본인의 아이디로 수정하세요)
rss_url = "https://v2.velog.io/rss/@agline"
feed = feedparser.parse(rss_url)

# 글을 저장할 폴더가 없으면 생성
if not os.path.exists("posts"):
    os.makedirs("posts")

for entry in feed.entries:
    # 파일 이름에서 특수문자 제거 (파일명으로 사용할 수 있게)
    file_name = entry.title.replace("/", "-").replace(":", "-") + ".md"
    file_path = os.path.join("posts", file_name)

    # 이미 존재하는 파일이면 건너뜀
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {entry.title}\n\n")
            f.write(f"게시일: {entry.published}\n")
            f.write(f"링크: {entry.link}\n\n")
            f.write("---\n\n")
            f.write(entry.description) # Velog RSS는 본문 전체를 포함함
        print(f"새로운 포스트 추가: {file_name}")
