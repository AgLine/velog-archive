import requests
import os

# 설정
VELOG_USERNAME = "agline" # 벨로그 아이디 입력

def get_velog_posts(username):
    url = 'https://api.velog.io/graphql'
    query = """
    query Posts($username: String!) {
        posts(username: $username) {
            title
            released_at
            updated_at
            body
            url_slug
            series {
                name
            }
        }
    }
    """
    variables = {'username': username}
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()['data']['posts']

def sync_posts():
    posts = get_velog_posts(VELOG_USERNAME)
    
    if not os.path.exists("posts"):
        os.makedirs("posts")

    for post in posts:
        # 1. 시리즈 확인 (없으면 No-Series 폴더)
        series_name = post['series']['name'] if post['series'] else "No-Series"
        series_name = series_name.replace("/", "-").replace(":", "-") # 폴더명 특수문자 제거
        
        folder_path = os.path.join("posts", series_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 2. 파일명 설정
        file_name = post['title'].replace("/", "-").replace(":", "-") + ".md"
        file_path = os.path.join(folder_path, file_name)

        # 3. 파일 생성 (이미 있으면 건너뜀 - 수동 관리 유지)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {post['title']}\n\n")
                f.write(f"게시일: {post['released_at']}\n")
                f.write(f"시리즈: {series_name}\n\n")
                f.write("---\n\n")
                f.write(post['body'])
            print(f"새 포스트 추가: [{series_name}] {post['title']}")

if __name__ == "__main__":
    sync_posts()
