# SpringBoot+React

게시일: Wed, 07 Aug 2024 05:47:33 GMT
링크: https://velog.io/@agline/SpringBootReact

---

<p><img alt="" src="https://velog.velcdn.com/images/agline/post/e2f5a393-a698-465c-8e08-5d291f745b19/image.png" /></p>
<p>매번 jsp를 통해 view를 만들었엇지만 react를 사용해보려 함</p>
<p><a href="https://sundries-in-myidea.tistory.com/71">https://sundries-in-myidea.tistory.com/71</a>
<a href="https://github.com/kantega/react-and-spring">https://github.com/kantega/react-and-spring</a></p>
<h3 id="개발환경">개발환경</h3>
<blockquote>
<p>SpringBoot 3.3.2
JAVA 17
Eclipse IDE
Node.js 20.16.0
maven</p>
</blockquote>
<h1 id="nodejs-설치">node.js 설치</h1>
<p><a href="https://nodejs.org/en/download/prebuilt-installer">https://nodejs.org/en/download/prebuilt-installer</a>
설치후 cmd에 node -v 입력
<img alt="" src="https://velog.velcdn.com/images/agline/post/f602ef45-0c13-4176-a596-c9e74bab8358/image.png" /></p>
<h1 id="스프링부트-프로젝트-생성">스프링부트 프로젝트 생성</h1>
<p><img alt="" src="https://velog.velcdn.com/images/agline/post/5e0aa87b-d422-4c09-8d10-d4b31097b0cd/image.png" />
<img alt="" src="https://velog.velcdn.com/images/agline/post/ca12e1f0-2c62-4620-9b85-826b84bceb33/image.png" /></p>
<h1 id="스프링으로-간단한-restapi-만들기">스프링으로 간단한 RestAPI 만들기</h1>
<pre><code>package com.example.react.ctrl;

import java.util.Date;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ApiCtrl {

    @GetMapping(&quot;/api/hello&quot;)
    public String hello(){
        return &quot;ㅎㅇ 현재 서버 시간 ::&quot; +new Date();
    }
}</code></pre><p><img alt="" src="https://velog.velcdn.com/images/agline/post/d4119b57-62b6-4e52-8c37-53591f91a306/image.png" /></p>
<h1 id="react-설치">React 설치</h1>
<p>cmd를 켜고 스프링부트의 폴더위치로 찾아감
<img alt="" src="https://velog.velcdn.com/images/agline/post/aa62375f-0083-461e-846f-2465e265860f/image.png" />
위 사진처럼 생성되어야함</p>
<pre><code>cd react
npx create-react-app frontend
cd frontend
npm start

# 필요한 모듈 설치 (현재 사용하지 않아서 설치하진않았음 이후 필요할 때 설치할 예정)
npm install bootstrap react-bootstrap --save # 부트스트랩 모듈
npm install react-router-dom --save # 라우터 모듈
npm install axios --save # 서버와 통신하기 위한 모듈
npm install maven # 메이븐 </code></pre><p>npm start를 누르면 react가 localhost:3000 으로 실행됨
<img alt="" src="https://velog.velcdn.com/images/agline/post/5e5d22df-221a-4bef-bff5-2c796537d1aa/image.png" /></p>
<h1 id="프록시-설정">프록시 설정</h1>
<p>빌드한 뒤 서버를 실행하면 프론트, 백엔드는 같은 포트로 동작하지만,
개발 시 React Dev Server(port: 3000), Spring Server(port: 8080)로 포트가 나뉘어 실행되기 때문에,
CORS를 방지하기 위해 프록시 설정이 필요</p>
<pre><code>&quot;proxy&quot;: &quot;http://localhost:9090”,</code></pre><p><img alt="" src="https://velog.velcdn.com/images/agline/post/404abb9e-b731-4d33-8675-a256894fd2c9/image.png" />
8080은 오라클이 사용중이어서 9090으로 바꿈</p>
<p>바꾼 후 SpringBoot와 react서버를 실행시키고
<img alt="" src="https://velog.velcdn.com/images/agline/post/cdbb24e3-7796-45da-9fc1-53bf53be56e2/image.png" />
다른포트로 실행시켜도 동일한 응답이 나옴</p>
<h1 id="applicationproperties">application.properties</h1>
<pre><code>spring.thymeleaf.prefix=classpath:/static/
spring.mvc.view.suffix=.html</code></pre><h1 id="react-화면에-적용해보기">react 화면에 적용해보기</h1>
<p>app.js 파일을 수정해 RestAPI값을 받고 출력</p>
<pre><code>import React, {useState, useEffect} from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
    const [message, setMessage] = useState(&quot;&quot;);

        useEffect(() =&gt; {
            fetch('/api/hello')
                .then(response =&gt; response.text())
                .then(message =&gt; {
                    setMessage(message);
                });
        },[])
  return (
    &lt;div className=&quot;App&quot;&gt;
      &lt;header className=&quot;App-header&quot;&gt;
        &lt;img src={logo} className=&quot;App-logo&quot; alt=&quot;logo&quot; /&gt;
        &lt;h1 className=&quot;App-title&quot;&gt;{message}&lt;/h1&gt;
        &lt;p&gt;
          Edit &lt;code&gt;src/App.js&lt;/code&gt; and save to reload.
        &lt;/p&gt;
        &lt;a
          className=&quot;App-link&quot;
          href=&quot;https://reactjs.org&quot;
          target=&quot;_blank&quot;
          rel=&quot;noopener noreferrer&quot;
        &gt;
          Learn React
        &lt;/a&gt;
      &lt;/header&gt;
    &lt;/div&gt;
  );
}

export default App;</code></pre><p><img alt="" src="https://velog.velcdn.com/images/agline/post/25a8dcb1-09cf-45a5-83cf-fe7698c4cf57/image.png" /></p>