# [Spring Boot WAR 배포] AWS EC2 + Tomcat 10.0.x+ JSP

게시일: Mon, 02 Jun 2025 07:45:57 GMT
링크: https://velog.io/@agline/Spring-Boot-WAR-%EB%B0%B0%ED%8F%AC-AWS-EC2-Tomcat-10.0.x-JSP

---

<h1 id="1-개요">1. 개요</h1>
<p>Spring Boot로 만든 프로젝트를 외부에서도 접근할 수 있게 만들고 싶었습니다.</p>
<p>지금까지는 로컬호스트(localhost)에서만 실행하고 확인했지만, 누구나 퍼블릭 IP로 접속할 수 있게 만들고 싶어서 AWS EC2와 Tomcat을 사용한 외부 배포를 시도했습니다.
내장 톰캣을 사용하는 JAR 배포도 가능하지만, 조직의 배포 정책이나 기존 인프라와의 호환성을 고려하여 WAR 배포를 선택했습니다.</p>
<p>이 글은 Spring Boot 프로젝트를 WAR 방식으로 빌드하고, EC2에 설치한 Tomcat에 배포해서 JSP 페이지를 외부에서 접근 가능하게 만드는 전체 과정을 정리한 기록입니다.</p>
<h1 id="2-개발-환경">2. 개발 환경</h1>
<ul>
<li><p>IDE: IntelliJ IDEA  </p>
</li>
<li><p>운영체제(OS): Amazon Linux 2023 (EC2 인스턴스)  </p>
</li>
<li><p>프레임워크: Spring Boot 3.5.0  </p>
</li>
<li><p>JDK 버전: 17 (Amazon Corretto)  </p>
</li>
<li><p>WAS: Apache Tomcat 10.1.41  </p>
</li>
<li><p>빌드 도구: Maven  </p>
</li>
<li><p>패키징 방식: WAR</p>
<h1 id="3-war-파일로-배포한-이유">3. war 파일로 배포한 이유</h1>
</li>
<li><p><strong>운영 환경과 유사한 구조 학습</strong>
실제 기업의 운영 환경에서는 외부 WAS(Web Application Server) 를 사용하는 경우가 많다.
이를 고려해 개발 단계부터 war 패키지를 외부 Tomcat에 배포함으로써, 운영 환경과 유사한 구조를 시뮬레이션하고자 했다.</p>
</li>
<li><p><strong>외부 톰캣 설정 및 배포 구조 직접 경험</strong>
jar로 실행하면 내장 톰캣이 자동으로 구동되지만, war로 배포할 경우 서버에 직접 Tomcat을 설치하고 설정해야 한다.
이 과정을 통해 톰캣의 구조, 로그 확인, context 설정 등을 직접 다뤄볼 수 있었다.</p>
</li>
<li><p><strong>다중 애플리케이션 배포 가능성 대비</strong>
향후 하나의 톰캣 서버에서 여러 개의 웹 애플리케이션을 운영할 가능성을 고려했다.
war 방식은 이러한 다중 애플리케이션 관리에 보다 유연하며, 공용 톰캣 환경에서 프로젝트를 분리하여 관리하기 용이하다.</p>
<h1 id="4-spring-boot-war-프로젝트-설정">4. Spring Boot war 프로젝트 설정</h1>
</li>
<li><p>pom.xml</p>
<pre><code>&lt;packaging&gt;war&lt;/packaging&gt;</code></pre></li>
<li><p>MyApplication.java</p>
<pre><code class="language-java">@SpringBootApplication
public class MyApplication extends SpringBootServletInitializer {
  public static void main(String[] args) {
      SpringApplication.run(MyApplication.class, args);
  }

  @Override
  protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
      return builder.sources(MyApplication.class);
  }
}
</code></pre>
</li>
</ul>
<pre><code>jar로 배포하면 실행하면서 내장 톰캣을 쓰기 때문에 서블릿 등록 같은 걸 자동으로 다 해준다. 
하지만 war로 배포하기 때문에 SpringBootServletInitializer를 상속받아야 한다.
SpringBootServletInitializer를 상속하는 이유는 외부 톰캣에서 이 앱을 제대로 시작할 수 있도록 도와주는 역할을 하기 때문이다.
즉, 톰캣한테 &quot;나는 서블릿이에요!&quot; 하고 알려주는 역할을 한다.

# 5. JSP 설정
- application.properties</code></pre><p>spring.mvc.view.prefix=/WEB-INF/jsp/
spring.mvc.view.suffix=.jsp</p>
<pre><code># 6. EC2 인스턴스 생성
- 인스턴스
![](https://velog.velcdn.com/images/agline/post/0f9c2391-8b2e-40bf-bcb3-bf1f9bf0b3fa/image.png)![](https://velog.velcdn.com/images/agline/post/46eeb10e-72b6-44f7-809d-d46d52932f96/image.png)![](https://velog.velcdn.com/images/agline/post/0fed7b9b-1825-4872-abec-81cbbd83f08d/image.png)![](https://velog.velcdn.com/images/agline/post/bf704f6a-4ba2-4e67-a369-220da43fd585/image.png)![](https://velog.velcdn.com/images/agline/post/25d9213d-8698-4a79-9e22-debe1872c334/image.png)

- 보안그룹 
![](https://velog.velcdn.com/images/agline/post/2f9da665-8b86-4e32-9656-a7ccb578f929/image.png)


# 7. EC2에 Java &amp; Tomcat 설치 및 기본 설정

- 자바 JDK17 설치
``` bash
sudo yum update -y   # Amazon Linux
sudo yum install java-17-amazon-corretto -y

java -version</code></pre><ul>
<li><p>tomcat10 설치
<a href="https://tomcat.apache.org/download-10.cgi">https://tomcat.apache.org/download-10.cgi</a>
core -&gt; tar.gz파일 다운</p>
<pre><code class="language-bash">tar -xvzf apache-tomcat-10.1.41.tar.gz #압축해제
mv apache-tomcat-10.1.41 tomcat10 # 디렉토리 이름을 접근하기 쉽게변경
cd tomcat10/bin #디렉토리 이동
chmod +x *.sh # .sh 확장자를 가진 모든 파일에 실행 권한 부여</code></pre>
</li>
<li><p>tomcat 실행포트 80으로 변경</p>
<pre><code class="language-bash">vi /home/ec2-user/tomcat9/conf/server.xml</code></pre>
<pre><code>&lt;Connector port=&quot;80&quot; protocol=&quot;HTTP/1.1&quot;
         connectionTimeout=&quot;20000&quot;
         redirectPort=&quot;8443&quot; /&gt;</code></pre><h1 id="8-배포">8. 배포</h1>
</li>
<li><p>war 파일 만들기
<img alt="" src="https://velog.velcdn.com/images/agline/post/99e4c03a-9407-435f-b935-8c6c47dc945d/image.png" /><img alt="" src="https://velog.velcdn.com/images/agline/post/4d72e3c9-df47-4504-912a-6a21ea119d81/image.png" />
target폴더 안에 war파일이 생성됨
생성된 war파일의 이름을 ROOT로 변경</p>
</li>
<li><p>/home/ec2-user/tomcat10/webapps/
현재있는 ROOT폴더를 삭제해주고 ROOT.war파일을 업로드
<img alt="" src="https://velog.velcdn.com/images/agline/post/b20335c7-6eeb-410b-a2a7-e6654b0bee6f/image.png" /></p>
</li>
<li><p>톰캣 재시작</p>
<pre><code class="language-bash">cd /home/ec2-user/tomcat10/bin
./shutdown.sh
./startup.sh</code></pre>
</li>
</ul>
<p>기존 webapps/ROOT 폴더가 남아있으면, 이 폴더가 우선 실행되기 때문에 기존 ROOT폴더는 삭제한다.
톰캣이 새 WAR 파일을 인식하고 자동으로 압축해제하며 배포한다.</p>
<h1 id="9-도메인연결">9. 도메인연결</h1>
<p>가비아에서 이벤트중인 도메인을 구입하여 진행했다.</p>
<ul>
<li><p>AWS Route 53 호스팅영역 생성
<img alt="" src="https://velog.velcdn.com/images/agline/post/8c028cbe-8ed9-452a-94d1-a81318ff5812/image.png" />
가비아의 네임서버 설정에 AWS 네임서버를 입력해준다.
<img alt="" src="https://velog.velcdn.com/images/agline/post/8321926e-e214-4c31-9ca1-9060b71eb920/image.png" /><img alt="" src="https://velog.velcdn.com/images/agline/post/e2cb761c-f3eb-44d5-997c-5beb6f24448a/image.png" /></p>
</li>
<li><p>AWS Route 53 레코드영역 생성
<img alt="" src="https://velog.velcdn.com/images/agline/post/a71617bc-6f51-47d5-90d4-c7238b4b9a79/image.png" /></p>
</li>
</ul>