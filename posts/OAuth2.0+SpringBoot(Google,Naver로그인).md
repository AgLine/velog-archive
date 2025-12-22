# OAuth2.0+SpringBoot(Google,Naver로그인)

게시일: Tue, 10 Sep 2024 06:20:38 GMT
링크: https://velog.io/@agline/OAuth2.0SpringBootGoogleNaver%EB%A1%9C%EA%B7%B8%EC%9D%B8

---

<h1 id="아직-작성중인글입니다">아직 작성중인글입니다.</h1>
<p>로그인 기능을 구현할 때 항상 단순히 문자열이 일치하는지만 확인하는 것으로 개발했었다.</p>
<p>최근 SNS 로그인을통해 기능을 구현해 보고 싶어 SpringBoot와 OAuth2.0를 연동하여 구현하고자 한다.</p>
<h1 id="1-프로젝트생성">1. 프로젝트생성</h1>
<p>Spring Initializr를 사용하여 프로젝트 생성</p>
<blockquote>
</blockquote>
<h4 id="--프로젝트메타데이터">- 프로젝트메타데이터</h4>
<p>Project: Maven
Language: Java
Spring Boot: 3.3.2
Group: com.example
Artifact: demo
Name: demo
Packaging: War
Java: 17</p>
<h4 id="--dependencies">- Dependencies</h4>
<p>Spring Web
Spring security
Spirng oauth2 client
MyBatis Framework
Oracle Driver (ojdbc8)
Lombok</p>
<h1 id="2-applicationproperties">2. application.properties</h1>
<pre><code>spring.application.name=security

server.port = 9090

spring.mvc.view.prefix=/WEB-INF/jsp/view/
spring.mvc.view.suffix=.jsp

spring.datasource.driver-class-name=oracle.jdbc.OracleDriver
spring.datasource.url=jdbc:oracle:thin:@localhost:1521/xe
spring.datasource.username=cinplus
spring.datasource.password=0000

mybatis.configuration.map-underscore-to-camel-case=true
mybatis.mapper-locations=classpath:mapper/**/*.xml

spring.profiles.include=oauth

#google login
spring.security.oauth2.client.registration.google.client-id=
spring.security.oauth2.client.registration.google.client-secret=
spring.security.oauth2.client.registration.google.scope=profile,email

#naver login
spring.security.oauth2.client.registration.naver.client-id=
spring.security.oauth2.client.registration.naver.client-secret=
spring.security.oauth2.client.registration.naver.scope=name,email
spring.security.oauth2.client.registration.naver.client-name=Naver
spring.security.oauth2.client.registration.naver.authorization-grant-type=authorization_code
spring.security.oauth2.client.registration.naver.redirect-uri=http://localhost:9090/login/oauth2/code/naver

#naver OAuth2 provider
spring.security.oauth2.client.provider.naver.authorization-uri=https://nid.naver.com/oauth2.0/authorize
spring.security.oauth2.client.provider.naver.token-uri=https://nid.naver.com/oauth2.0/token
spring.security.oauth2.client.provider.naver.user-info-uri=https://openapi.naver.com/v1/nid/me

spring.security.oauth2.client.provider.naver.user-name-attribute=response</code></pre><h1 id="3-프로젝트-디렉토리-구조">3. 프로젝트 디렉토리 구조</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/5cb1c8a5-ff7a-4259-b9f7-76fb439ab0a2/image.png" /></p>
<h1 id="4-소스코드">4. 소스코드</h1>
<h2 id="securityconfigjava">SecurityConfig.java</h2>
<pre><code class="language-JAVA">package com.example.security.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;

import lombok.RequiredArgsConstructor;

import com.example.security.oauth.PrincipalOauth2UserService;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity(securedEnabled = true)
@RequiredArgsConstructor
public class SecurityConfig {

    private final PrincipalOauth2UserService principalOauth2UserService;
    private final CorsConfig corsConfig;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception{
        http.csrf(AbstractHttpConfigurer::disable);
        http.addFilter(corsConfig.corsFilter());
        http.authorizeHttpRequests(au -&gt; au.anyRequest().permitAll());
        http.oauth2Login(
                oauth -&gt; oauth.loginPage(&quot;/loginForm&quot;)
                        .defaultSuccessUrl(&quot;/home&quot;)
                        .userInfoEndpoint(configurer -&gt; {
                            configurer.userService(principalOauth2UserService);
                        })
        );
        return http.build();
    }
}</code></pre>
<ul>
<li>@Configuration : 이 클래스가 설정 클래스임을 나타냄 Spring은 이 클래스를 사용해 빈(bean)을 생성하고 관리</li>
<li>@EnableWebSecurity : Spring Security를 활성화, 스프링 시큐리티 필터가 스프링 필터체인에 등록</li>
<li>@EnableMethodSecurity(securedEnabled = true) : 애노테이션 사용가능 여부에 대한 속성<pre><code>@Secured(&quot;ROLE_ADMIN&quot;) //
@GetMapping(&quot;/info&quot;)
public @ResponseBody String info() {
  return &quot;개인정보&quot;;
}</code></pre>이런 식으로 컨트롤러의 함수에 @Secured 애노테이션을 붙여주면, 애노테이션에 인자로 받은 권한이 유저에게 있을 때만 실행하도록 할 수 있음 </li>
<li>@RequiredArgsConstructor : 클래스에 정의된 final 필드를 생성자 주입 방식으로 자동 초기화 여기서는 principalOauth2UserService와 corsConfig가 대상</li>
<li>principalOauth2UserService : OAuth2 로그인 과정에서 사용자 정보를 처리하는 서비스</li>
<li>corsConfig : CORS(Cross-Origin Resource Sharing) 설정을 위한 구성 클래스</li>
<li>@Bean : 이 메서드가 반환하는 객체가 Spring 컨텍스트에서 관리되는 빈으로 등록</li>
<li>SecurityFilterChain : Spring Security의 필터 체인을 정의하는 객체</li>
<li>HttpSecurity : 보안 설정을 구성하는 데 사용되는 주요 클래스</li>
<li>http.csrf(AbstractHttpConfigurer::disable) : CSRF(Cross-Site Request Forgery) 보호를 비활성화</li>
<li>http.addFilter(corsConfig.corsFilter()) : CORS 설정을 위한 필터를 필터 체인에 추가</li>
<li>http.authorizeHttpRequests : 들어오는 HTTP 요청에 대한 접근 제어</li>
<li>anyRequest().permitAll() : 모든 요청 허가</li>
<li>http.oauth2Login : OAuth2 기반 로그인 설정을 시작</li>
<li>oauth.loginPage(&quot;/loginForm&quot;) : 로그인 페이지로 사용될 URL을 지정, 사용자가 로그인되지 않은 상태에서 보호된 페이지에 접근하면 이 URL로 리다이렉트 </li>
<li>defaultSuccessUrl(&quot;/home&quot;) : 로그인 성공 후 리다이렉트될 기본 URL을 설정</li>
<li><h1 id="마무리">마무리</h1>
</li>
</ul>
<h1 id="참고자료">참고자료</h1>
<p><a href="https://velog.io/@juice/Springboot-Security-%EA%B5%AC%EA%B8%80-%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EA%B5%AC%ED%98%84">https://velog.io/@juice/Springboot-Security-%EA%B5%AC%EA%B8%80-%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EA%B5%AC%ED%98%84</a>
<a href="https://velog.io/@shon5544/Spring-Security-4.-%EA%B6%8C%ED%95%9C-%EC%B2%98%EB%A6%AC">https://velog.io/@shon5544/Spring-Security-4.-%EA%B6%8C%ED%95%9C-%EC%B2%98%EB%A6%AC</a></p>