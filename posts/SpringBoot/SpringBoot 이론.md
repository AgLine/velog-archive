# SpringBoot 이론

게시일: 2025-12-26T08:45:35.637Z
시리즈: SpringBoot

---

# SpringBoot

# 1. **Spring Framework란 무엇인가요?**

- 
    
    Java 엔터프라이즈급 애플리케이션을 쉽게 만들 수 있도록 도와주는 프레임워크이다.
    

## 1-1. **Framework란?**

- 
    
    개발자가 애플리케이션을 만들 때 따라야 하는 일정한 규칙을 틀로 만들어 놓은 것
    
    프레임워크는 기본적인 구조와 미리 만들어진 기능들을 제공
    
    규칙과 구조를 제공하여 개발자가 일관된 방식으로 애플리케이션을 만들 수 있게 도와줌
    
    코드의 가독성이 높아지고, 협업 시 다른 개발자가 코드를 쉽게 이해할 수 있음
    
    프레임워크의 핵심 목표는 효율성
    

## 1-2. 엔터프라이즈급 애플리케이션

- 
    
    '엔터프라이즈급' 이라는 용어는 IT 및 소프트웨어 개발 분야에서 자주 사용되며, **대규모 조직(회사, 정부 기관 등)의 비즈니스 요구 사항을 충족하도록 설계된 시스템이나 애플리케이션**을 의미
    
    | **특성** | **설명** |
    | --- | --- |
    | **확장성 (Scalability)** | 사용자 수, 데이터 양, 트래픽 증가 등 대규모 성장을 원활하게 수용할 수 있는 능력. 시스템을 쉽게 확장하거나 축소할 수 있어야 합니다. |
    | **안정성 (Reliability) / 가용성 (Availability)** | 장시간 동안 오류 없이 지속적으로 작동할 수 있는 능력. 장애 발생 시에도 서비스가 중단되지 않거나(고가용성), 신속하게 복구될 수 있어야 합니다. |
    | **보안 (Security)** | 민감한 기업 데이터와 사용자 정보를 보호하기 위한 강력한 인증, 인가, 데이터 암호화 메커니즘을 갖추어야 합니다. |
    | **성능 (Performance)** | 많은 사용자와 대량의 트랜잭션을 처리할 때에도 빠르고 효율적으로 응답할 수 있는 처리 속도. |
    | **통합 용이성 (Integrability)** | 기존의 다른 비즈니스 시스템 (예: CRM, ERP, 레거시 시스템)과 쉽게 연결하고 데이터를 주고받을 수 있는 능력. |
    | **유지보수성 (Maintainability)** | 시스템의 복잡도가 높더라도 버그 수정, 기능 추가, 업데이트 등의 작업이 용이하도록 잘 구조화되고 문서화되어 있어야 합니다. |
    | **트랜잭션 관리 (Transaction Management)** | 비즈니스 로직에서 데이터의 일관성을 보장하는 복잡한 트랜잭션을 안전하게 처리할 수 있는 기능 (예: 은행 시스템의 이체). |

# **2. Spring 프레임워크를 사용하는 장점은 무엇인가요?**

- 
    1. **경량성 (POJO):** EJB와 달리 순수 자바 객체(POJO)를 사용하여 코드의 복잡성을 낮추고 테스트 용이성을 높입니다.
    2. **제어의 역전(Inversion of Control, IoC)**: Spring은 IoC를 사용하여 객체의 생명주기와 종속성을 관리합니다.
    3. **관점 지향 프로그래밍(Aspect-Oriented Programming, AOP)**: Spring은 로깅, 보안 등의 횡단 관심사를 분리하기 위해 AOP를 지원합니다.
    4. **PSA (서비스 추상화):** 트랜잭션, 캐시, 데이터 접근 등 기술이 바뀌어도 코드는 유지되도록 일관된 인터페이스를 제공합니다.
    5. **생태계 및 생산성 (Spring Boot):** 자동 설정, 내장 서버, 방대한 라이브러리(Security, Data JPA 등)를 통해 비즈니스 로직 개발에만 집중할 수 있는 환경을 제공합니다.

## 2-1. EJB

- 
    
    Enterprise Java Beans → 비즈니스 로직 하나를 짜려면 프레임워크가 강제하는 상속, 인터페이스 구현을 해야함.
    
    ```java
    // 프레임워크의 클래스를 '상속' 받아야 함 (강제성)
    public class BlogPostService extends EJBServiceBase implements SessionBean {
    
        // 내가 짠 적 없는 생명주기 메서드들을 강제로 구현해야 함 (불필요한 코드)
        public void ejbCreate() { ... }
        public void ejbRemove() { ... }
        public void ejbActivate() { ... }
    
        // 실제 비즈니스 로직은 여기 조금...
        public void writePost() {
            // ...
        }
    }
    ```
    

## 2-2. **POJO**

- 
    
    Plain Old Java Object → 그냥 평범한 옛날 자바 객체
    
    ```java
    // 아무것도 상속받지 않음. 그냥 순수 자바 객체(POJO).
    public class BlogPostService {
    
        // 오직 비즈니스 로직에만 집중
        public void writePost() {
            // ...
        }
    }
    ```
    

## 2-3. PSA

- 
    
    PSA = 기술을 갈아끼우기 쉽게 만들어주는 표준 인터페이스(어댑터).
    
    - **PSA가 없다면 (끔찍한 상황):**
        - 만약 `JDBC`를 쓰면: `connection.commit()` 이라고 코드를 짜야 함
        - 만약 `JPA`를 쓰면: `entityManager.getTransaction().commit()` 이라고 코드를 다 바꿔야 함
        - **기술을 바꿀 때마다 비즈니스 로직 코드를 다 뜯어고쳐야 함**
    - **PSA가 있다면 (Spring):**
        - 그냥 `@Transactional`만 붙임
        - Spring이 알아서 판단 → "어? 지금 JPA 쓰네? 그럼 내가 JPA 방식으로 처리해줄게."
        - 나중에 MyBatis로 기술을 바꿔도 코드는 **`@Transactional`** 그대로 두면 됨
        - Spring이 알아서 "어? 이번엔 MyBatis네? 그쪽 방식으로 처리해줄게." 라고 맞춰줌

# 3. **Spring 프레임워크의 핵심 모듈은 무엇인가요?**

- 
    
    Spring은 **Core/Context**를 통해 객체를 관리하고, **Web MVC**로 API 요청을 처리하며, **ORM/TX** 모듈로 DB 트랜잭션을 보장합니다. 또한 **AOP**로 부가 기능을 분리하고, **Test** 모듈로 안정성을 확보하는 구조입니다.
    
    **1. Core Container (코어 컨테이너) - 프레임워크의 기반**
    
    - **Spring Core & Beans:** 프레임워크의 가장 기본적인 부분으로 **IoC(제어의 역전)**와 **DI(의존성 주입)** 기능을 제공합니다 (`BeanFactory` 등).
    - **Spring Context:** Core 위에 구축되어 국제화(다국어 메시지 관리), 이벤트 전파(컴포넌트 간 방송 시스템 → 느슨한 결합), 리소스 로딩(파일 읽기 편의 기능) 등 엔터프라이즈급 기능을 추가로 제공합니다 (`ApplicationContext`).
    - **Spring SpEL (Expression Language):** 런타임에 객체 그래프를 조회하고 조작할 수 있는 강력한 표현 언어를 지원합니다.
        - **내가 값을 정할 수 없을 때:** (DB에서 가져온 값, 외부 설정 파일 값, 다른 객체의 현재 상태 등)
        - **자바 코드를 수정하고 컴파일하기 싫을 때:** 설정(Annotation)만 바꾸면 로직이 바뀌게 하고 싶을 때.
        - **Spring Security(권한 관리)**
    
    ```java
    @Component
    public class ReferenceSample {
    
        // 'userService'라는 Bean의 'userName' 필드 값을 가져옴
        @Value("#{userService.userName}")
        private String name;
    
        // 'userService'의 getAge() 메소드를 실행해서 그 결과를 대문자로 변환
        // null 방지를 위해 안전 탐색 연산자(?.) 사용 가능
        @Value("#{userService.getUserRegion()?.toUpperCase()}")
        private String region; 
    }
    
    @Service
    public class PostService {
    
        // "메소드 파라미터로 들어온 id가 10보다 작거나, 관리자(ADMIN) 권한이 있어야 실행 가능"
        @PreAuthorize("#id < 10 or hasRole('ROLE_ADMIN')")
        public void deletePost(long id) {
            // 로직...
        }
    
        // "파라미터로 받은 post 객체의 작성자(writer)가 현재 로그인한 유저 이름과 같아야 함"
        @PreAuthorize("#post.writer == authentication.name")
        public void editPost(Post post) {
            // 로직...
        }
    }
    ```
    
    **2. Data Access / Integration (데이터 접근 및 통합)**
    
    - **Spring JDBC:** 반복적인 JDBC 코드를 제거하고 데이터베이스 종류별로 에러 코드를 Spring의 예외 계층으로 변환합니다.
    - **Spring ORM:** JPA(Hibernate), MyBatis 등 널리 사용되는 ORM 프레임워크와의 통합 계층을 제공합니다.
    - **Spring TX (Transactions):** 모든 POJO에 대해 선언적(`@Transactional`) 및 프로그래밍 방식의 트랜잭션 관리를 지원합니다.
    
    **3. Web (웹 계층)**
    
    - **Spring Web MVC:** 서블릿(Servlet) 기반의 웹 애플리케이션 및 RESTful 웹 서비스 구축을 위한 MVC 구현을 제공합니다.
    - **Spring WebFlux:** 비동기 및 논블로킹(Non-blocking) 리액티브 웹 애플리케이션 개발을 지원합니다. (Spring 5+)
        - 리액티브하게 짜려면 결과값을 무조건 Mono나 Flux로 감싸야 함
        - **Non-blocking (논블로킹):** "안 막힘". DB나 네트워크 작업이 끝날 때까지 멍하니 기다리지 않고 다른 일을 먼저 처리하는 방식입니다.
        - **Reactive (리액티브):** 데이터가 들어오면 그때그때 반응해서 처리한다는 뜻입니다. (유튜브 스트리밍처럼 데이터가 흐르는 대로 처리)
        
        ```jsx
        public Mono<User> updateName(String id) {
            // 1. 찾으라고 시킴 (기다리지 않고 바로 다음 줄로 넘어감)
            return repository.findById(id)
                // 2. "혹시 데이터가 도착하면, 이름을 홍길동으로 바꿔라"라고 예약
                .map(user -> {
                    user.setName("홍길동");
                    return user;
                })
                // 3. "그 작업이 끝나면, 저장을 실행해라"라고 예약
                .flatMap(savedUser -> repository.save(savedUser));
        }
        ```
        
        **Mono & Flux (리액티브의 데이터 그릇)** → 이 리액티브 개념을 구현하기 위해 사용하는 두 가지 리턴 타입.
        
        📦 Mono (모노): 데이터가 0개 또는 1개일 때 사용. (단일 결과)
        
        예: ID로 회원 찾기, 저장 완료 신호
        
        🌊 Flux (플럭스): 데이터가 0개 ~ 무한대(N개)일 때 사용. (흐르는 물줄기)
        
        예: 회원 목록 전체, 실시간 로그, 주식 시세
        
    
    **4. AOP (Aspect Oriented Programming)**
    
    - **Spring AOP:** 관점 지향 프로그래밍을 지원하여, 로깅이나 보안 같은 횡단 관심사(Cross-cutting Concerns)를 비즈니스 로직에서 분리해 모듈화합니다.
    
    **5. Test (테스트)**
    
    - **Spring Test:** JUnit, TestNG, Mockito 등을 사용하여 Spring 컴포넌트의 단위 테스트 및 통합 테스트를 지원합니다. (`MockMvc`, `TestContext` 등)

# 4. 제어의 역전(Inversion of Control, IoC)이란 무엇인가요?

- 
    
    객체의 생성부터 소멸까지의 생명주기 관리와 의존성 결정 권한을 개발자가 아닌 외부(스프링 프레임워크)에 위임하는 설계 원칙입니다.
    
    Spring에서는 이를 의존성 주입(DI)을 통해 구체화하며 이를 통해 객체 간의 결합도(Coupling)를 낮추고 유연한 코드와 테스트 용이성을 확보할 수 있습니다.
    

# 5. 의존성 주입(Dependency Injection, DI)이란 무엇인가요?

- 
    
    의존성 주입(DI)은 객체가 필요로 하는 의존 객체를 직접 생성하는 것이 아니라 외부(스프링 컨테이너)로 부터 주입받는 기법입니다.
    
    DI를 통해 객체 간의 결합도를 낮추어 유연한 변경이 가능해지고, 단위 테스트가 쉬워집니다. 
    주입 방식으로는 생성자, 세터, 필드 주입이 있는데, 스프링에서는 객체의 불변성을 보장하기 위해 생성자 주입(Constructor Injection)을 주로 권장합니다
    

# 6. Spring에서 의존성 주입의 종류는 무엇인가요?

- 
    
    생성자 주입: 생성자를 통해 종속성을 제공합니다.
    
    세터 주입: Setter 메서드를 통해 종속성을 제공합니다.
    
    필드 주입: 종속성이 필드에 직접 주입됩니다. (테스트 및 유지보수 문제로 인해 권장되지 않음).
    

## 6-1. `@RequiredArgsConstructor` 를 쓰는 이유

- 
    - **Getter/Setter는 반복 노동이다?**  → 맞습니다. 그래서 롬복(`@Data`, `@Getter`)이 대신 해줍니다.
    - **`@Autowired`와 생성자 둘 다 DI다?** → 맞습니다. 방법만 다를 뿐 목적은 같습니다.
    - **`@Autowired`는 강한 결합이다? →** 정확히는 **"프레임워크(Spring)와의 강한 결합"**입니다. 스프링이 없으면 못 쓰는 코드가 되니까요.
    - **생성자는 느슨한 결합이다?** → 스프링이 없어도 자바 코드로 동작하니까 유연하고 테스트가 쉽습니다.
    - **그래서 `@RequiredArgsConstructor`를 쓴다?** → 생성자 코드 짜기 귀찮으니까, 롬복한테 "final 붙은 애들 모아서 생성자 만들어줘!"라고 시키는 것입니다.
    
    스프링에서는 **생성자 주입**이 테스트 용이성과 불변성 때문에 권장되는데요. 생성자 코드를 매번 직접 작성하면 코드가 길어지고 번거롭기 때문에,
    **Lombok의 `@RequiredArgsConstructor`를 사용하여 반복적인 코드를 줄이고 깔끔하게 의존성을 주입**받고 있습니다.
    

# **7. Spring Bean이란 무엇인가요?**

- 
    
    Spring이 대신 만들어서 가지고 있는 객체를 **Bean**이라고 부르며, 이 Bean들이 모여 있는 박스를 **Spring Container(IoC Container)**라고 합니다.
    
    보통 자바에서 객체를 사용할 때는 `MyService service = new MyService();`처럼 직접 생성함 → 하지만 Spring에서는 개발자가 직접 객체를 생성(`new`)하지 않고, **Spring에게 객체 생성과 관리 권한을 넘김**
    

# **8. Spring Bean을 정의하는 방법은 무엇인가요?**

- 
    1. 어노테이션 방식
    
    클래스 위에 `@Component`를 붙이면 Spring이 "오, 이 클래스는 내가 관리해야 할 Bean이구나!"라고 알아차리고 자동으로 객체를 생성합니다.
    
    `@Service`, `@Repository`, `@Controller`는 모두 내부적으로 `@Component`를 포함하고 있습니다.
    
    “내부적으로 포함하고 있다.”는 말은 자바의 **메타 어노테이션(Meta-Annotation)**이라는 개념을 알면 쉽게 이해할 수 있습니다.
    
    객체지향 언어에서 클래스가 다른 클래스를 **상속**받는 것처럼, Spring에서는 **어노테이션이 다른 어노테이션을 가질 수 있습니다.**
    
    1. 자바 기반 설정 방식 (외부 라이브러리 사용 시)
    
    ```java
    @Configuration
    public class AppConfig {
        @Bean
        public RestTemplate restTemplate() {
            return new RestTemplate(); // 이 리턴되는 객체가 Bean이 됩니다.
        }
    }
    ```
    

### Spring Bean 요약

- 
    - **Bean:** Spring이 관리하는 객체.
    - **Container:** Bean들을 담고 있는 박스.
    - **등록 방법:** 보통은 클래스에 `@Component`를 붙이고, 특별한 경우 `@Configuration` 안에서 `@Bean`으로 직접 등록함.
    - **장점:** 객체 생성을 Spring이 대신해주니 결합도가 낮아지고 유지보수가 쉬워짐.

# 9. **Spring Bean 생명주기는 어떻게 되나요?**

- 
    
    스프링 IoC 컨테이너 생성 → 스프링 빈 생성 → 의존관계 주입 → 초기화 콜백 메소드 호출 → 사용 → 소멸 전 콜백 메소드 호출 → 스프링 종료 
    

### 빈 생명주기 콜백방법

- 
    1. **설정 정보에 초기화 메소드, 종료 메소드 지정**
        
        ```java
        public class ExampleBean {
         
            public void initialize() throws Exception {
                // 초기화 콜백 (의존관계 주입이 끝나면 호출)
            }
         
            public void close() throws Exception {
                // 소멸 전 콜백 (메모리 반납, 연결 종료와 같은 과정)
            }
        }
         
        @Configuration
        class LifeCycleConfig {
         
            @Bean(initMethod = "initialize", destroyMethod = "close")
            public ExampleBean exampleBean() {
                // 생략
            }
        }
        ```
        
        장점: 
        
        - 메소드명을 자유롭게 부여 가능, 스프링 코드에 의존하지 않음
        - 설정 정보를 사용하기 때문에 코드를 커스터마이징 할 수 없는 외부라이브러리에서도 적용 가능
        - 내가 코드를 수정할 수 없는 **남이 만든 라이브러리**를 Bean으로 등록할 때만 사용
        
        단점:
        
        - Bean 지정시 initMethod와 destoryMethod를 직접 지정해야 하기에 번거로움
        - 문자열로 메서드명을 적어야 해서 **오타 나기 쉽고**, 이름 바꿀 때 **두 군데를 고쳐야 해서** 귀찮고 위험
    2. **@PostConstruct, @PreDestroy 어노테이션 지원**
        
        ```java
        import javax.annotation.PostConstruct;
        import javax.annotation.PreDestroy;
         
        public class ExampleBean {
         
            @PostConstruct
            public void initialize() throws Exception {
                // 초기화 콜백 (의존관계 주입이 끝나면 호출)
            }
         
            @PreDestroy
            public void close() throws Exception {
                // 소멸 전 콜백 (메모리 반납, 연결 종료와 같은 과정)
            }
        }
        ```
        
        장점:
        
        - **최신 스프링에서 가장 권장하는 방법,** 어노테이션 하나만 붙이면 되므로 매우 편리, 컴포넌트 스캔과 잘어울림
        - 패키지가 javax.annotation.xxx → 스프링에 종속적인 기술이 아닌 JSR-250이라는 자바 표준. 따라서 스프링이 아닌 다른 컨테이너에서도 동작
        
        단점:
        
        - 커스터마이징이 불가능한 외부 라이브러리에서 적용이 불가능
        
        Spring Bean Life Cycle을 이해하면 더 안정적이고 효율적인 애플리케이션을 설계할 수 있음 
        초기화와 소멸 단계에서 리소스를 효과적으로 관리함으로써 성능 최적화와 자원 관리 측면에서 큰 이점을 얻을 수 있음
        
    

# 10. **@Component, @Service, @Repository, @Controller 애노테이션의 차이점은 무엇인가요?**

- 
    - **@Component**: Spring이 관리하는 모든 구성 요소에 대한 일반적인 스테레오타입 애노테이션입니다.
    - **@Service**: 서비스 레이어 구성 요소를 위한 @Component의 특수화입니다.
    - **@Repository**: DAO(Data Access Object) 구성 요소를 위한 @Component의 특수화로, 예외 번역 등의 추가 기능을 제공합니다.
    - **@Controller**: 웹 컨트롤러 구성 요소를 위한 @Component의 특수화입니다.

# **11. Spring Boot란 무엇인가요?**

- 
    
    복잡한 설정 없이 즉시 실행 가능한 Spring 애플리케이션을 쉽고 빠르게 만들 수 있게 해주는 도구
    

# **12. Spring Boot를 사용하는 장점은 무엇인가요?**

- 
    
    **1. 설정의 자동화 (Convention over Configuration)**
    
    과거 Spring에서는 XML 파일을 수백 줄씩 작성해야 했던 복잡한 설정을 자동으로 처리합니다. 라이브러리만 추가하면 Spring Boot가 필요한 빈(Bean)들을 알아서 등록해 줍니다.
    
    **2. 내장 서버를 통한 독립 실행 (Standalone)**
    
    Tomcat 웹 서버(WAS)가 프레임워크 내부에 내장되어 있습니다. 덕분에 별도의 서버 설치 과정 없이 `.jar` 파일 하나만 실행하면 어디서든 애플리케이션이 돌아갑니다.
    
    **3. 스타터(Starter)를 통한 의존성 관리**
    
    여러 라이브러리의 버전 호환성을 일일이 확인할 필요가 없습니다. `spring-boot-starter-web`처럼 용도에 맞는 **Starter** 하나만 추가하면 관련 패키지들이 최적의 버전 조합으로 한 번에 세팅됩니다.
    
    **4. 운영 준비 완료 (Production Ready)**
    
    애플리케이션이 실제 운영 환경에서 잘 돌아가고 있는지 확인하는 기능을 기본 제공합니다.
    
    - **Actuator:** 앱의 상태(Health check), 메트릭, 덤프 등을 모니터링할 수 있습니다.
    - **외부 설정:** 동일한 코드를 수정 없이 개발/테스트/운영 환경에 맞춰 설정값만 바꿔 실행할 수 있습니다.

# 13. Spring Boot 애플리케이션을 만드는 방법은 무엇인가요?

- 
    1. **Spring Initializr 사용 (가장 권장되는 방법)**
    - 가장 빠르고 표준적인 방법입니다. [start.spring.io](https://start.spring.io/) 사이트에 접속하여 클릭 몇 번으로 프로젝트를 생성할 수 있습니다.
    - 설정이 완료된 `.zip` 파일을 다운로드하여 IDE(IntelliJ, Eclipse 등)에서 열기만 하면 됩니다.
    1. **수동 생성 및 코드 작성**
    - 빌드 파일 설정 (`pom.xml` 또는 `build.gradle`)
    - 메인 클래스 작성
    
    ```java
    @SpringBootApplication // 이 클래스가 스프링 부트 앱의 시작점임을 알림
    public class MySpringBootApplication {
        public static void main(String[] args) {
            // 애플리케이션을 실행하는 핵심 메서드
            SpringApplication.run(MySpringBootApplication.class, args);
        }
    }
    ```
    

# 14. **@SpringBootApplication 란 무엇인가요?**

- 
    
    여러 핵심 어노테이션을 합쳐놓은 **합성 어노테이션(Meta-annotation)**입니다. 클래스 파일을 열어보면 아래 세 가지가 핵심입니다.
    
    1. **`@SpringBootConfiguration`**
    - 스프링의 `@Configuration`과 동일한 역할을 합니다.
    - 해당 클래스가 스프링의 **설정 클래스**임을 선언하며 빈(Bean) 등록을 돕습니다.
    1. **`@ComponentScan`**
    - 이 어노테이션이 붙은 클래스의 **패키지를 기준으로 하위 패키지까지** 전부 훑어서 `@Component`, `@Service`, `@Repository`, `@Controller` 등이 붙은 클래스들을 찾아 빈으로 등록합니다.
    - **주의:** 그래서 메인 클래스는 항상 프로젝트의 최상단 패키지에 위치해야 합니다.
    1. **`@EnableAutoConfiguration`** 
    - 스프링 부트의 핵심인 **'자동 설정'을 활성화**합니다.
    - 미리 정의된 수많은 설정 중 현재 내 프로젝트에 필요한 것들만 골라서 자동으로 세팅해 줍니다.

# 15. **Spring Data JPA란 무엇인가요?**

- 
    
    "JPA는 자바 객체와 관계형 데이터베이스 사이의 패러다임 불일치를 해결하기 위한 자바의 ORM 표준 사양입니다." → (정의)
    
    "반복적인 SQL 작성 없이 객체 중심으로 개발할 수 있게 도와주며, 실제 구현체로는 하이버네이트(Hibernate)를 주로 사용합니다." → (특징 및 구현체)
    
    "결과적으로 개발자는 비즈니스 로직에 더 집중할 수 있고, 유지보수와 생산성을 크게 높일 수 있다는 장점이 있습니다." → (기대 효과)
    
    - **자바 ORM 표준**: 자바 객체와 관계형 데이터베이스(RDB) 사이의 차이를 메워주는 **ORM(Object-Relational Mapping)** 기술의 표준 사양
    - **인터페이스 모음**: JPA 자체가 구현체는 아니며, 자바에서 데이터베이스를 어떻게 관리할지 정의한 **인터페이스의 집합**
    - **패러다임 불일치 해결**: 객체지향 구조와 테이블 중심의 RDB 구조 사이의 간극을 자동으로 해결
    - **SQL 중심에서 객체 중심으로**: 개발자가 SQL을 직접 작성하는 대신, 자바 객체를 다루듯 DB를 다룰 수 있음
    - **생산성 극대화**: 반복적인 CRUD(Create, Read, Update, Delete)용 SQL을 JPA가 자동으로 생성해주어 개발 속도가 매우 빠름
    - **유지보수 향상**: 필드가 변경되어도 SQL을 일일이 수정할 필요가 없어 유지보수가 쉬움
    - **특정 DB 종속성 탈피**: 설정만 바꾸면 MySQL, Oracle, H2 등 다양한 DB로 쉽게 교체할 수 있는 **방언(Dialect)** 기능을 제공
    - **영속성 컨텍스트(Persistence Context)**: 객체를 효율적으로 관리하기 위한 일종의 메모리 공간을 두어, 성능 최적화(1차 캐시, 쓰기 지연 등)를 도움
    - **하이버네이트(Hibernate)**: JPA라는 표준 사양을 실제로 구현한 가장 대표적이고 대중적인 프레임워크가 바로 하이버네이트
    - **데이터 중심에서 도메인 중심으로**: 데이터베이스 테이블 설계에 매몰되지 않고, 서비스의 핵심 로직(도메인 모델)에 더 집중

# **16. Spring Repository란 무엇인가요?**

- 
    
    Spring Repository는 **데이터 접근 로직을 인터페이스로 추상화한 계층**입니다.
    
    가장 큰 장점은 개발자가 SQL이나 반복적인 매핑 코드를 직접 작성하지 않아도 **메서드 이름만으로 쿼리를 생성하거나 기본적인 CRUD를 처리**할 수 있습니다.
    
    결과적으로 데이터베이스가 바뀌거나 접근 방식이 변해도 **서비스 계층의 코드를 보호**할 수 있고 보일러플레이트 코드 제거하여 생산성을 높여주는 역할을 합니다.
    
    - **데이터 접근 계층의 표준화**: DB에 데이터를 넣고 빼는 방식을 일관된 인터페이스로 통일
    - **인터페이스 선언**: 개발자가 직접 클래스를 구현(implements)할 필요 없이, 인터페이스만 만들면 Spring Data JPA가 실행 시점에 대리객체(Proxy)를 만들어 기능을 수행
    - **메서드 이름이 곧 쿼리**: `findByName`처럼 메서드 이름을 규칙에 맞게 지으면, JPA가 이를 해석해 자동으로 `SELECT ... WHERE name = ?` 쿼리를 실행
    - **보일러플레이트 코드 제거**: JDBC를 쓸 때 거치던 `Connection` 열기, `PreparedStatement` 생성, `ResultSet` 매핑 같은 반복적인 코드 삭제
    - **예외 변환기 역할**: DB마다 다른 복잡한 에러(SQLException 등)를 스프링이 이해할 수 있는 공통 에러(`DataAccessException`)로 변환
    - **계층 분리(Decoupling)**: 서비스 로직(비즈니스 규칙)이 특정 DB 처리 기술에 얽매이지 않게 중간에서 방어막 역할
    - **기본 CRUD 제공**: `save()`, `findById()`, `findAll()`, `delete()` 같은 필수 기능을 상속만으로 즉시 사용
    - **페이징 및 정렬의 간소화**: 복잡한 페이징 쿼리를 직접 짤 필요 없이, `Pageable` 객체 하나만 파라미터로 넘기면 처리 끝
    - **유연한 쿼리 작성**: 메서드 이름만으로 부족할 땐 `@Query` 어노테이션을 통해 JPQL이나 생 SQL을 직접 작성가능
    - **테스트 용이성**: 인터페이스 구조이기 때문에, 실제 DB 연결 없이 가짜(Mock) 객체를 갈아 끼워 비즈니스 로직만 테스트 가능

# 17. **Spring MVC란 무엇인가요?**

- 
    
    중앙 컨트롤러(DispatcherServlet)를 중심으로 요청을 처리하며 데이터(Model)·화면(View)·로직(Controller)을 분리하여 관리하는 효율적인 웹 프레임워크입니다.
    

## 17-1. MVC

- 
    - **Model (모델):** 애플리케이션의 **데이터**와 비즈니스 로직을 담당 (무엇을 보여줄 것인가?)
    - **View (뷰):** 사용자에게 보여지는 **화면** 인터페이스(HTML 등)를 담당 (어떻게 보여줄 것인가?)
    - **Controller (컨트롤러):** 사용자의 요청을 받아 모델과 뷰를 **연결**해주는 다리 역할 (어디로 보낼 것인가?)

## 17-2. Spring MVC의 동작 흐름

- 
    1. **클라이언트의 요청:** 사용자가 URL을 입력하여 요청을 보냄
    2. **DispatcherServlet 접수:** 모든 요청은 중앙 컨트롤러인 DispatcherServlet이 받음
    3. **컨트롤러 찾기:** Handler Mapping을 통해 해당 요청을 처리할 컨트롤러를 찾음
    4. **컨트롤러 실행:** 컨트롤러는 로직을 수행하고 결과 데이터(Model)와 이동할 페이지 정보(View Name)를 반환
    5. **뷰 찾기:** ViewResolver가 반환된 뷰 이름을 바탕으로 실제 화면 파일을 찾음
    6. **응답 반환:** 뷰에 모델 데이터를 입혀서 최종적인 HTML을 사용자의 브라우저로 보냄