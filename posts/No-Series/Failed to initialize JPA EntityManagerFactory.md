# Failed to initialize JPA EntityManagerFactory

게시일: 2024-08-14T02:09:56.672Z
시리즈: No-Series

---

### Failed to initialize JPA EntityManagerFactory 오류는 Hibernate에서 지정한 Dialect 클래스명을 찾을 수 없을 때 발생하는 에러

org.hibernate.dialect.Oracle11gDialect가 인식되지 않는 문제일 가능성이 큼

Hibernate 버전이 Oracle11gDialect를 지원하지 않는 경우도 있음
스프링 부트 3.x 이상에서는 Hibernate 6.x 버전이 기본으로 포함되며, 이 버전에서는 Oracle11gDialect 대신 OracleDialect를 사용하는 것이 권장

# 해결방법

spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.Oracle11gDialect가 올바른 설정이지만 
오류가 발생할 경우 application.properties를 아래와 같이 변경


```
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.OracleDialect
```
