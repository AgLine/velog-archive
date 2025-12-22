# React SPA + Nginx 도커 배포 시 404 에러 해결법

게시일: 2025-07-29T11:52:16.119Z
시리즈: No-Series

---

프론트엔드에서 React Router를 사용하는 SPA 앱을 Nginx로 배포할 때, 다음과 같은 문제가 발생할 수 있습니다.

✅ http://localhost:3000/ 는 잘 뜨는데,
❌ http://localhost:3000/test 은 404 Not Found 오류 발생

❓ 왜 이런 문제가 발생할까?
React는 브라우저 라우팅을 사용하는 SPA 앱입니다.
하지만 Nginx는 기본적으로 정적 파일 경로(/test, /about 등)를 그대로 찾으려 합니다.

/test을 요청 → Nginx는 usr/share/nginx/html/test이라는 정적 파일이 있다고 착각함 → ❌ 404 에러 발생

✅ 해결 방법
SPA 앱의 모든 경로를 index.html로 리다이렉트하게 Nginx 설정을 수정하면 됩니다.

# 📁 1. nginx.conf 파일 작성
frontend/nginx.conf 파일 생성:
```
server {
  listen 80;
  server_name localhost;

  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri /index.html;
  }
}
```

# 🐳 2. React 앱용 Dockerfile 수정
frontend/Dockerfile:

```
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```
# 🚀 3. 배포순서
```
# 기존 컨테이너 종료
docker-compose down

# 프론트엔드 이미지만 새로 빌드
docker-compose build --no-cache frontend

# 다시 컨테이너 실행
docker-compose up -d frontend

```

# ❓ 왜 try_files $uri /index.html;을 쓰면 해결되는걸까?
```
location / {
  try_files $uri /index.html;
}

```
"요청한 경로에 해당하는 파일이 없으면, index.html을 대신 리턴해줘!"

1. /test 요청이 들어오면
→ Nginx는 /usr/share/nginx/html/test 파일을 찾음

2. 파일이 없다면
→ 대신 /index.html을 반환

3. index.html 안에는 React 앱을 구동하는 JS 코드가 있음

4. 이 JS 코드가 실행되며,
→ React Router가 현재 경로(/test)를 감지하고 해당 페이지를 렌더링

**Nginx는 index.html만 제공하고, 나머진 JS가 처리하는 구조**

# ❓ 왜 Nginx를 사용하는가?
| 이유                  | 설명                                             |
| ------------------- | ---------------------------------------------- |
| 정적 파일 서빙에 최적화       | HTML, CSS, JS 파일을 빠르고 가볍게 전달                   |
| Node 서버 불필요         | 운영 시 Express나 Node.js 서버를 계속 띄울 필요 없음          |
| SPA 라우팅 대응 가능       | 모든 경로를 `index.html`로 리디렉션하여 React Router 작동 보장 |
| 보안, 캐싱, HTTPS 등 확장성 | 리버스 프록시, 보안 헤더, 인증서 설정 등에 강력함                  |
| 가벼운 배포 환경 구성        | Docker 멀티 스테이지로 빌드 + 서빙 환경 분리 가능               |
