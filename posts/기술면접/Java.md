# Java

게시일: 2026-01-24T10:04:35.012Z
시리즈: 기술면접

---

### **Java의 주요 특징 5가지를 설명하시오.**

- 객체지향 프로그래밍: 클래스와 객체 기반, 캡슐화/상속/다형성
- 플랫폼 독립성: JVM에서 실행, WORA(Write Once, Run Anywhere)
- 자동 메모리 관리: Garbage Collector가 자동으로 메모리 회수
- 멀티스레딩 지원: 동시 작업 처리 가능
- 보안성: 포인터 미지원, 강력한 타입 체크

### **JDK, JRE, JVM의 차이점과 관계를 설명하시오.**

- JVM: 바이트코드를 실행하는 가상머신
- JRE: JVM + 표준 라이브러리 (실행 환경)
- JDK: JRE + 개발도구(컴파일러, 디버거 등)
- 관계: JDK ⊃ JRE ⊃ JVM

### **public static void main(String[] args)의 각 키워드 의미는?**

- public: 모든 곳에서 접근 가능
- static: 객체 생성 없이 클래스 레벨에서 호출
- void: 반환값 없음
- main: 프로그램 시작점(entry point)
- String[] args: 명령행 인자 배열

### **Java의 데이터 타입을 분류하고 각각의 크기를 설명하시오.답안:**

- 기본 타입(Primitive):
    - 정수: byte(1), short(2), int(4), long(8)
    - 실수: float(4), double(8)
    - 문자: char(2)
    - 논리: boolean(1)
- 참조 타입(Reference): 클래스, 인터페이스, 배열

### **변수의 종류 4가지와 특징을 설명하시오.답안:**

- 지역변수: 메서드 내 선언, 메서드 종료시 소멸
- 인스턴스 변수: 객체마다 독립적, 힙 메모리
- 클래스 변수(static): 모든 객체가 공유, 메서드 영역
- 매개변수: 메서드 호출시 전달되는 값

### **접근 제어자 4가지의 접근 범위를 표로 정리하시오.**

- private: 같은 클래스
- default: 같은 패키지
- protected: 같은 패키지 + 상속받은 클래스
- public: 모든 곳

| 제어자 | 같은 클래스 | 같은 패키지 | 자식 클래스 | 전체 |
| --- | --- | --- | --- | --- |
| private | O | X | X | X |
| default | O | O | X | X |
| protected | O | O | O | X |
| public | O | O | O | O |

### **생성자(Constructor)의 특징과 규칙은?**

- 클래스 이름과 동일
- 반환 타입이 없음
- 객체 생성시 자동 호출
- 오버로딩 가능
- 명시하지 않으면 기본 생성자 자동 생성

### **this와 super 키워드의 차이는?답안:**

- this: 현재 객체 참조, 인스턴스 변수/메서드 접근
- super: 부모 클래스 참조, 부모의 생성자/메서드 호출
- this(): 같은 클래스의 다른 생성자 호출
- super(): 부모 클래스의 생성자 호출

### **static 키워드의 의미와 사용 예시는?답안:**

- 클래스 레벨에서 공유되는 멤버
- 객체 생성 없이 접근 가능
- 메모리에 한 번만 할당

```java
public class Counter {
    static int count = 0;  // 모든 객체가 공유
    static void increment() {
        count++;
    }
}
Counter.increment();  // 객체 없이 호출
```

### **final 키워드의 3가지 사용처와 의미는?**

- final 변수: 상수, 값 변경 불가
- final 메서드: 오버라이딩 불가
- final 클래스: 상속 불가

```java
final int MAX = 100;
final void method() {}
final class FinalClass {}
```

### **형변환(Casting)의 종류와 예시를 작성하시오.**

- 자동 형변환(Promotion): 작은 타입 → 큰 타입

```java
int i = 100;
long l = i;  // 자동 변환
```

- 강제 형변환(Casting): 큰 타입 → 작은 타입

```java
double d = 3.14;
int i = (int)d;  // 명시적 변환, 손실 발생
```

### **Wrapper 클래스와 Boxing/Unboxing을 설명하시오.**

- Wrapper 클래스: 기본 타입을 객체로 감쌈
    - int → Integer, double → Double 등
- Auto Boxing: 기본 타입 → Wrapper 객체
- Auto Unboxing: Wrapper 객체 → 기본 타입

```java
Integer obj = 10;  // Auto Boxing
int num = obj;     // Auto Unboxing
```

### **패키지(Package)의 목적과 import 사용법은?**

- 목적: 클래스를 그룹화하여 관리, 이름 충돌 방지
- 선언: package com.example.project;
- import: 다른 패키지의 클래스 사용

```java
import java.util.ArrayList;
import java.util.*;  // 패키지의 모든 클래스
```

### **연산자 우선순위 상위 5개는?**

1. 괄호: ()
2. 증감 연산자: ++, --
3. 산술 연산자: *, /, %
4. 산술 연산자: +, -
5. 비교 연산자: <, >, <=, >=

### **삼항 연산자의 문법과 사용 예시는?답안:**

```java
// 문법: 조건식 ? 참일때값 : 거짓일때값
int max = (a > b) ? a : b;
String result = (score >= 60) ? "합격" : "불합격";
```

### 객체지향 (16-30)

### **객체지향의 4대 특징을 설명하시오.**

- 캡슐화: 데이터와 메서드를 하나로 묶고 은닉
- 상속: 기존 클래스의 특성을 물려받음
- 다형성: 같은 이름으로 다양한 동작 구현
- 추상화: 공통 특성을 추출하여 표현

### **캡슐화의 장점과 구현 방법은?**

- 장점: 정보 은닉, 유지보수 용이, 결합도 감소
- 구현: private 변수 + public getter/setter

```java
public class Person {
    private String name;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

### **상속의 장점과 단점은?**

- 장점: 코드 재사용, 계층적 분류, 유지보수 용이
- 단점: 결합도 증가, 부모 변경시 자식 영향
- Java는 단일 상속만 지원 (다중 상속 불가)

### **오버로딩(Overloading)과 오버라이딩(Overriding)의 차이는?**

- 오버로딩: 같은 이름, 다른 매개변수 (컴파일 시점)

```java
void print(int x) {}
void print(String x) {}
```

- 오버라이딩: 부모 메서드 재정의 (실행 시점)

```java
@Override
public void method() {}
```

### **다형성(Polymorphism)을 구현하는 방법 2가지는?**

- 오버로딩: 같은 이름, 다른 시그니처
- 오버라이딩: 부모 메서드 재정의

```java
Animal animal = new Dog();  // 업캐스팅
animal.sound();  // Dog의 sound() 호출 (동적 바인딩)
```

### **추상 클래스(Abstract Class)의 특징은?**

- abstract 키워드로 선언
- 추상 메서드(구현부 없음) 포함 가능
- 객체 생성 불가
- 일반 메서드와 변수도 가질 수 있음

```java
abstract class Animal {
    abstract void sound();  // 추상 메서드
    void eat() {}  // 일반 메서드
}
```

### **인터페이스(Interface)의 특징은?**

- 모든 메서드가 public abstract (Java 8 이전)
- 모든 변수가 public static final
- 다중 구현 가능
- Java 8부터 default, static 메서드 가능

```java
interface Flyable {
    void fly();
    default void land() {}  // Java 8+
}
```

### **추상 클래스와 인터페이스의 차이점을 표로 정리하시오.**

| 구분 | 추상 클래스 | 인터페이스 |
| --- | --- | --- |
| 다중 상속 | 불가 | 가능 |
| 구현 메서드 | 가능 | default만 가능 |
| 변수 | 모든 종류 | static final만 |
| 생성자 | 가능 | 불가 |
| 용도 | is-a 관계 | can-do 관계 |

### **업캐스팅과 다운캐스팅을 설명하시오.**

- 업캐스팅: 자식 → 부모 (자동 형변환)

```java
Animal animal = new Dog();  // 업캐스팅
```

- 다운캐스팅: 부모 → 자식 (명시적, instanceof 확인)

```java
if (animal instanceof Dog) {
    Dog dog = (Dog)animal;  // 다운캐스팅
}
```

### **instanceof 연산자의 용도와 사용법은?**

- 객체가 특정 클래스의 인스턴스인지 확인
- 다운캐스팅 전 타입 확인에 사용

```java
if (obj instanceof String) {
    String str = (String)obj;
}
```

### **Object 클래스의 주요 메서드 5가지는?**

- toString(): 객체의 문자열 표현
- equals(): 객체 내용 비교
- hashCode(): 해시코드 반환
- getClass(): 클래스 정보 반환
- clone(): 객체 복제

### **equals()와 ==의 차이점을 설명하시오.**

- ==: 참조 주소 비교 (동일성)
- equals(): 객체 내용 비교 (동등성)

```java
String s1 = new String("hello");
String s2 = new String("hello");
s1 == s2;        // false (다른 객체)
s1.equals(s2);   // true (같은 내용)
```

### **hashCode()와 equals()의 관계는?**

- equals()가 true면 hashCode()도 같아야 함
- HashMap, HashSet에서 중요
- 둘 다 오버라이드하거나 둘 다 하지 말아야 함

```java
@Override
public boolean equals(Object o) { ... }
@Override
public int hashCode() { ... }
```

### **내부 클래스(Inner Class)의 종류 4가지는?**

- 인스턴스 내부 클래스: 외부 인스턴스와 연결
- 정적 내부 클래스: static, 외부 인스턴스 불필요
- 지역 내부 클래스: 메서드 내부에 정의
- 익명 내부 클래스: 이름 없이 즉석 정의

### **익명 클래스(Anonymous Class)의 사용 예시는?**

```java
// 인터페이스 구현
Runnable r = new Runnable() {
    @Override
    public void run() {
        System.out.println("Running");
    }
};

// 이벤트 리스너
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("Clicked");
    }
});
```

### 컬렉션 프레임워크 (31-40)

### **컬렉션 프레임워크의 주요 인터페이스 3가지는?**

- List: 순서 있음, 중복 허용
- Set: 순서 없음, 중복 불허
- Map: key-value 쌍, key는 중복 불허

### **ArrayList와 LinkedList의 차이점은?**

| 구분 | ArrayList | LinkedList |
| --- | --- | --- |
| 구조 | 배열 기반 | 노드 기반 |
| 조회 | O(1) 빠름 | O(n) 느림 |
| 삽입/삭제 | O(n) 느림 | O(1) 빠름 |
| 메모리 | 연속적 | 분산적 |

### **Vector와 ArrayList의 차이점은?**

- Vector: 동기화(synchronized), 멀티스레드 안전, 느림
- ArrayList: 비동기화, 단일스레드 환경, 빠름
- 대부분의 경우 ArrayList 사용 권장

### **HashSet, TreeSet, LinkedHashSet의 차이는?**

- HashSet: 순서 없음, O(1), 가장 빠름
- TreeSet: 정렬됨, O(log n), Red-Black Tree
- LinkedHashSet: 삽입 순서 유지, O(1)

### **HashMap의 동작 원리를 설명하시오.**

- 해시 함수로 키의 해시코드 계산
- 해시코드를 버킷 인덱스로 변환
- 충돌 발생시 체이닝(Linked List) 사용
- Java 8부터 버킷 크기 8 이상시 트리로 변환
- 시간 복잡도: 평균 O(1), 최악 O(n)→O(log n)

### **HashMap과 Hashtable의 차이는?**

- HashMap: 동기화X, null 허용, 빠름
- Hashtable: 동기화O, null 불허, 느림
- 동기화 필요시 ConcurrentHashMap 사용 권장

### **Comparable과 Comparator의 차이는?**

- Comparable: 기본 정렬, compareTo() 구현

```java
class Person implements Comparable<Person> {
    public int compareTo(Person p) {
        return this.age - p.age;
    }
}
```

- Comparator: 다양한 정렬, compare() 구현

```java
Collections.sort(list, new Comparator<Person>() {
    public int compare(Person p1, Person p2) {
        return p1.name.compareTo(p2.name);
    }
});
```

**Q38. Iterator와 향상된 for문의 차이는?**

- Iterator: 순회 중 요소 삭제 가능

```java
Iterator<String> it = list.iterator();
while(it.hasNext()) {
    String s = it.next();
    if(condition) it.remove();
}
```

- 향상된 for: 간결, 삭제 불가

```java
for(String s : list) {
    System.out.println(s);
}
```

### **Stack과 Queue의 특징과 구현 클래스는?**

- Stack: LIFO, push/pop/peek

```java
Stack<Integer> stack = new Stack<>();
stack.push(1);
stack.pop();
```

- Queue: FIFO, offer/poll/peek

```java
Queue<Integer> queue = new LinkedList<>();
queue.offer(1);
queue.poll();
```

### **Collections 클래스의 주요 메서드는?**

```java
Collections.sort(list);           // 정렬
Collections.reverse(list);        // 역순
Collections.shuffle(list);        // 섞기
Collections.max(list);            // 최대값
Collections.min(list);            // 최소값
Collections.frequency(list, obj); // 빈도
Collections.binarySearch(list, key); // 이진 탐색
```

### 예외 처리 및 기타 (41-50)

### **예외(Exception)의 종류와 차이점은?**

- Checked Exception: 컴파일 시점 체크, 처리 강제
    - IOException, SQLException 등
- Unchecked Exception: 런타임 시점, 처리 선택
    - RuntimeException, NullPointerException 등
- Error: 시스템 레벨, 처리 불가
    - OutOfMemoryError, StackOverflowError 등

### **try-catch-finally의 실행 순서는?**

```java
try {
    // 예외 발생 가능 코드
} catch (Exception e) {
    // 예외 처리 (예외 발생시)
} finally {
    // 항상 실행 (자원 해제 등)
}
```

- finally는 return, break 문 있어도 실행됨
- try-with-resources 사용 권장

### **try-with-resources 구문을 설명하시오.**

- Java 7부터 지원, 자동으로 자원 해제
- AutoCloseable 인터페이스 구현 필요

```java
try (FileReader fr = new FileReader("file.txt");
     BufferedReader br = new BufferedReader(fr)) {
    String line = br.readLine();
} // 자동으로 close() 호출
```

### **throw와 throws의 차이는?**

- throw: 예외를 직접 발생시킴

```java
if (age < 0) {
    throw new IllegalArgumentException("나이는 음수일 수 없습니다");
}
```

- throws: 메서드가 예외를 던질 수 있음을 선언

```java
public void readFile() throws IOException {
    // 파일 읽기
}
```

### **사용자 정의 예외를 만드는 방법은?**

```java
public class CustomException extends Exception {
    public CustomException() {
        super();
    }
    
    public CustomException(String message) {
        super(message);
    }
    
    public CustomException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### **String, StringBuilder, StringBuffer의 차이는?**

| 구분 | String | StringBuilder | StringBuffer |
| --- | --- | --- | --- |
| 가변성 | 불변 | 가변 | 가변 |
| 동기화 | - | 없음 | 있음 |
| 속도 | 느림 | 빠름 | 보통 |
| 용도 | 변경 적음 | 단일스레드 | 멀티스레드 |

### **String 클래스의 주요 메서드를 나열하시오.**

```java
String s = "Hello World";
s.length();              // 11
s.charAt(0);             // 'H'
s.substring(0, 5);       // "Hello"
s.indexOf("World");      // 6
s.replace("World", "Java"); // "Hello Java"
s.toUpperCase();         // "HELLO WORLD"
s.toLowerCase();         // "hello world"
s.trim();                // 공백 제거
s.split(" ");            // ["Hello", "World"]
s.equals("Hello World"); // true
```

### **== 와 equals()로 String 비교시 차이는?**

```java
String s1 = "hello";
String s2 = "hello";
String s3 = new String("hello");

s1 == s2;        // true (같은 리터럴, String Pool)
s1 == s3;        // false (다른 객체)
s1.equals(s3);   // true (같은 내용)
```

### **제네릭(Generic)의 장점과 사용법은?**

- 장점: 타입 안정성, 형변환 불필요, 코드 재사용

```java
// 제네릭 클래스
class Box<T> {
    private T item;
    public void set(T item) { this.item = item; }
    public T get() { return item; }
}

// 사용
Box<String> box = new Box<>();
box.set("Hello");
String s = box.get();  // 형변환 불필요

// 제네릭 메서드
public <T> void printArray(T[] array) {
    for(T element : array) {
        System.out.println(element);
    }
}
```

### **Enum(열거형)의 특징과 사용법은?**

- 고정된 상수 집합 정의
- type-safe, 싱글톤 보장

```java
public enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY;
    
    public boolean isWeekend() {
        return this == SATURDAY || this == SUNDAY;
    }
}

// 사용
Day today = Day.MONDAY;
switch(today) {
    case MONDAY:
        System.out.println("월요일");
        break;
}

// 메서드
Day.values();     // 모든 값 배열
Day.valueOf("MONDAY"); // 문자열로 값 얻기
today.ordinal();  // 순서(인덱스)
```