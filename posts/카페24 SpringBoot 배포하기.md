# 카페24 SpringBoot 배포하기

게시일: Fri, 17 May 2024 19:02:15 GMT
링크: https://velog.io/@agline/%EC%B9%B4%ED%8E%9824-SpringBoot-%EB%B0%B0%ED%8F%AC%ED%95%98%EA%B8%B0

---

<h1 id="1-war파일로-패키징한다는-코드-추가하기">1. war파일로 패키징한다는 코드 추가하기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/9e42902d-29d6-4239-a077-e0fe57148b45/image.png" /></p>
<pre><code>&lt;packaging&gt;war&lt;/packaging&gt;</code></pre><h1 id="2-clean-install-차례로-누르기">2. clean, install 차례로 누르기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/a1eb9381-666a-453d-a2b6-2782d4f6f82f/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/387b726a-92b2-44ca-b34b-1c1d4bb09442/image.png" />
빌드를 성공적으로 마치면</p>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/bbda867a-d22d-4ef7-8461-62c3fed482d0/image.png" />
target폴더안에 war파일 생성</p>
<h1 id="3-해당파일의-폴더로가서-이름-rootwar로-바꾸기">3. 해당파일의 폴더로가서 이름 ROOT.war로 바꾸기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/06b011fc-466a-446f-b312-16a6b2f83f32/image.png" /></p>
<h1 id="4-파일질라-설치하기">4. 파일질라 설치하기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/5fc02b05-19d3-401f-96a0-0926f9c927c8/image.png" />
FTP비밀번호 입력 (DB비밀번호와동일)
연결해서 /tomcat/webapp 폴더안에 ROOT.war파일 전송
<img alt="" src="https://velog.velcdn.com/images/agline/post/adf94925-6092-43df-8d88-eb75bc44961f/image.png" /></p>
<h1 id="5-putty-설치하기">5. putty 설치하기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/ea15d534-f95c-434a-9765-80756f9d096b/image.png" />
open 누르고 본인아이디, FTP비밀번호(DB비밀번호와동일) 차례대로 입력</p>
<pre><code>cd /webapp/tomcat                    ROOT.war이 있는 폴더로 이동
jar xvf ROOT.war                    ROOT.war파일 압축해제
cd                                    처음위치로이동
./tomcat/bin/shutdown.sh            
./tomcat/bin/startup.sh                톰캣재시작    </code></pre><h1 id="6-카페24-나의서비스관리로-이동하기">6. 카페24 나의서비스관리로 이동하기</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/ff041a29-46ca-48a9-a801-8b9e8b7c630e/image.png" />
설정하기 누르고 본인의 서버아이피 추가</p>