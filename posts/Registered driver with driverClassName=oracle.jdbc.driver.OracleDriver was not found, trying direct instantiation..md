# Registered driver with driverClassName=oracle.jdbc.driver.OracleDriver was not found, trying direct instantiation.

게시일: Mon, 05 Aug 2024 04:44:21 GMT
링크: https://velog.io/@agline/Registered-driver-with-driverClassNameoracle.jdbc.driver.OracleDriver-was-not-found-trying-direct-instantiation

---

<p>ERROR이 발생했던것은 아니지만 WARN으로 표기됨
Oracle9 버전이후로는 oracle.jdbc.OracleDriver 로 사용</p>
<h2 id="해결방법">해결방법</h2>
<p>application.properties에서 DB정보가 적혀있는 부분 중</p>
<p>oracle.jdbc.driver.OracleDriver &gt;&gt; oracle.jdbc.OracleDriver</p>
<p>수정하면 해결 됨</p>