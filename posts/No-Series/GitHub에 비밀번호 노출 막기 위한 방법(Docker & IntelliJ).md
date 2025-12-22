# GitHub에 비밀번호 노출 막기 위한 방법(Docker & IntelliJ)

게시일: 2025-07-21T06:48:57.723Z
시리즈: No-Series

---

✅ 왜 이걸 하게 되었는가?
React + Spring Boot + PostgreSQL 프로젝트를 Docker로 구성하고 GitHub에 올리는 과정에서,
docker-compose.yml이나 application.yml 같은 설정 파일에 비밀번호가 그대로 하드코딩되어 있었고
"도커랑 깃허브 연동했는데, 비밀번호까지 같이 올라가버리면…?"라는 생각을 하게 되었다.

GitHub에 그대로 커밋되면 누구든지 내 DB 접속 정보를 볼 수 있는 위험한 상태이기 때문에
이 문제를 막기 위해 아래 2가지 방법으로 안전하게 구성했습니다.

# 1. docker-compose.yml 비밀번호 숨기기 (.env)
- 위험한 예: 환경변수 직접 작성
  ```
  environment:
    POSTGRES_USER: myuser
    POSTGRES_PASSWORD: mypass
  ```
➡ 이렇게 하면 docker-compose.yml을 커밋할 때 비밀번호가 노출됨 ❌

### 해결 방법: .env 파일로 분리하기
``` 
environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```
그리고 .env 파일을 따로 만들어줍니다:

### .env (절대 깃허브에 올리면 안 됨)
```
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
```
마지막으로 .gitignore에 .env 추가:
![](https://velog.velcdn.com/images/agline/post/50fb7d4d-fcae-4eee-a8de-02b42c9436cb/image.png)

이렇게 하면 깃허브에 올려도 비밀번호는 제외되고,
Docker는 .env 파일을 읽어서 환경변수로 설정해준다.

# 2. IntelliJ 실행 시 비밀번호 숨기기
Spring Boot에서 application.yml에 비밀번호를 하드코딩하는 것도 위험합니다.

- 위험한 예
  ```
  spring:
    datasource:
      url: jdbc:postgresql://localhost:5432/postgres
      username: myuser
      password: mypass
  ```
### 해결 방법: 환경변수 사용 (${})
```
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
```
이제 IntelliJ에서 이 환경변수들을 직접 설정해줘야 합니다.

### IntelliJ 환경변수 설정 방법
우측 상단 Run/Debug Configurations 클릭
![](https://velog.velcdn.com/images/agline/post/ac5e54cd-bf76-4a05-9188-8c442d8f2c32/image.png)

실행할 Spring Boot 애플리케이션 선택

Environment variables 항목 클릭

아래처럼 작성:
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/postgres;SPRING_DATASOURCE_USERNAME=myuser;SPRING_DATASOURCE_PASSWORD=mypass
![](https://velog.velcdn.com/images/agline/post/922b9a08-bd9c-4c2d-99fb-2d020787c9b9/image.png)

이렇게 하면 로컬에서도 문제없이 실행되고,GitHub에도 비밀번호는 올라가지 않습니다!

# 정리 요약
| 구분                   | 처리 방법                          | 효과             |
| -------------------- | ------------------------------ | -------------- |
| `docker-compose.yml` | `.env` 파일로 분리 + `.gitignore`   | 깃허브 비밀번호 노출 방지 |
| `application.yml`    | `${}` 변수 처리 + IntelliJ에서 직접 설정 | 개발 환경에서도 보안 유지 |