# GitHub에 비밀번호 노출 막기 위한 방법(Docker & IntelliJ)

게시일: Mon, 21 Jul 2025 06:48:57 GMT
링크: https://velog.io/@agline/GitHub%EC%97%90-%EB%B9%84%EB%B0%80%EB%B2%88%ED%98%B8-%EB%85%B8%EC%B6%9C-%EB%A7%89%EA%B8%B0-%EC%9C%84%ED%95%9C-%EB%B0%A9%EB%B2%95Docker-IntelliJ

---

<p>✅ 왜 이걸 하게 되었는가?
React + Spring Boot + PostgreSQL 프로젝트를 Docker로 구성하고 GitHub에 올리는 과정에서,
docker-compose.yml이나 application.yml 같은 설정 파일에 비밀번호가 그대로 하드코딩되어 있었고
&quot;도커랑 깃허브 연동했는데, 비밀번호까지 같이 올라가버리면…?&quot;라는 생각을 하게 되었다.</p>
<p>GitHub에 그대로 커밋되면 누구든지 내 DB 접속 정보를 볼 수 있는 위험한 상태이기 때문에
이 문제를 막기 위해 아래 2가지 방법으로 안전하게 구성했습니다.</p>
<h1 id="1-docker-composeyml-비밀번호-숨기기-env">1. docker-compose.yml 비밀번호 숨기기 (.env)</h1>
<ul>
<li>위험한 예: 환경변수 직접 작성<pre><code>environment:
  POSTGRES_USER: myuser
  POSTGRES_PASSWORD: mypass</code></pre>➡ 이렇게 하면 docker-compose.yml을 커밋할 때 비밀번호가 노출됨 ❌</li>
</ul>
<h3 id="해결-방법-env-파일로-분리하기">해결 방법: .env 파일로 분리하기</h3>
<pre><code>environment:
  POSTGRES_USER: ${POSTGRES_USER}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}</code></pre><p>그리고 .env 파일을 따로 만들어줍니다:</p>
<h3 id="env-절대-깃허브에-올리면-안-됨">.env (절대 깃허브에 올리면 안 됨)</h3>
<pre><code>POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass</code></pre><p>마지막으로 .gitignore에 .env 추가:
<img alt="" src="https://velog.velcdn.com/images/agline/post/50fb7d4d-fcae-4eee-a8de-02b42c9436cb/image.png" /></p>
<p>이렇게 하면 깃허브에 올려도 비밀번호는 제외되고,
Docker는 .env 파일을 읽어서 환경변수로 설정해준다.</p>
<h1 id="2-intellij-실행-시-비밀번호-숨기기">2. IntelliJ 실행 시 비밀번호 숨기기</h1>
<p>Spring Boot에서 application.yml에 비밀번호를 하드코딩하는 것도 위험합니다.</p>
<ul>
<li>위험한 예<pre><code>spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/postgres
    username: myuser
    password: mypass</code></pre><h3 id="해결-방법-환경변수-사용-">해결 방법: 환경변수 사용 (${})</h3>
<pre><code>spring:
datasource:
  url: ${SPRING_DATASOURCE_URL}
  username: ${SPRING_DATASOURCE_USERNAME}
  password: ${SPRING_DATASOURCE_PASSWORD}</code></pre>이제 IntelliJ에서 이 환경변수들을 직접 설정해줘야 합니다.</li>
</ul>
<h3 id="intellij-환경변수-설정-방법">IntelliJ 환경변수 설정 방법</h3>
<p>우측 상단 Run/Debug Configurations 클릭
<img alt="" src="https://velog.velcdn.com/images/agline/post/ac5e54cd-bf76-4a05-9188-8c442d8f2c32/image.png" /></p>
<p>실행할 Spring Boot 애플리케이션 선택</p>
<p>Environment variables 항목 클릭</p>
<p>아래처럼 작성:
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/postgres;SPRING_DATASOURCE_USERNAME=myuser;SPRING_DATASOURCE_PASSWORD=mypass
<img alt="" src="https://velog.velcdn.com/images/agline/post/922b9a08-bd9c-4c2d-99fb-2d020787c9b9/image.png" /></p>
<p>이렇게 하면 로컬에서도 문제없이 실행되고,GitHub에도 비밀번호는 올라가지 않습니다!</p>
<h1 id="정리-요약">정리 요약</h1>
<table>
<thead>
<tr>
<th>구분</th>
<th>처리 방법</th>
<th>효과</th>
</tr>
</thead>
<tbody><tr>
<td><code>docker-compose.yml</code></td>
<td><code>.env</code> 파일로 분리 + <code>.gitignore</code></td>
<td>깃허브 비밀번호 노출 방지</td>
</tr>
<tr>
<td><code>application.yml</code></td>
<td><code>${}</code> 변수 처리 + IntelliJ에서 직접 설정</td>
<td>개발 환경에서도 보안 유지</td>
</tr>
</tbody></table>