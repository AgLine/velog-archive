# Failed to initialize JPA EntityManagerFactory

게시일: Wed, 14 Aug 2024 02:09:56 GMT
링크: https://velog.io/@agline/Failed-to-initialize-JPA-EntityManagerFactory

---

<h3 id="failed-to-initialize-jpa-entitymanagerfactory-오류는-hibernate에서-지정한-dialect-클래스명을-찾을-수-없을-때-발생하는-에러">Failed to initialize JPA EntityManagerFactory 오류는 Hibernate에서 지정한 Dialect 클래스명을 찾을 수 없을 때 발생하는 에러</h3>
<p>org.hibernate.dialect.Oracle11gDialect가 인식되지 않는 문제일 가능성이 큼</p>
<p>Hibernate 버전이 Oracle11gDialect를 지원하지 않는 경우도 있음
스프링 부트 3.x 이상에서는 Hibernate 6.x 버전이 기본으로 포함되며, 이 버전에서는 Oracle11gDialect 대신 OracleDialect를 사용하는 것이 권장</p>
<h1 id="해결방법">해결방법</h1>
<p>spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.Oracle11gDialect가 올바른 설정이지만 
오류가 발생할 경우 application.properties를 아래와 같이 변경</p>
<pre><code>spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.OracleDialect</code></pre>