# mybatis bad SQL grammar []] with root cause

게시일: Mon, 29 Jul 2024 12:03:05 GMT
링크: https://velog.io/@agline/mybatis-bad-SQL-grammar-with-root-cause

---

<p>sql문만 돌리면 잘 작동하는데 mybatis에서 자꾸 문법이 잘못되었다고 뜸</p>
<pre><code>SELECT * 
  FROM EXAMPLE;</code></pre><p>끝에 세미콜론 찍으면 안됨</p>
<pre><code>SELECT * 
  FROM EXAMPLE</code></pre><p>지우고 다시 실행하면 정상적으로 작동</p>