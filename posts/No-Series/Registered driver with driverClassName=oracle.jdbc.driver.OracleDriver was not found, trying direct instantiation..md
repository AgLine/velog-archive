# Registered driver with driverClassName=oracle.jdbc.driver.OracleDriver was not found, trying direct instantiation.

게시일: 2024-08-05T04:44:21.946Z
시리즈: No-Series

---

ERROR이 발생했던것은 아니지만 WARN으로 표기됨
Oracle9 버전이후로는 oracle.jdbc.OracleDriver 로 사용
## 해결방법
application.properties에서 DB정보가 적혀있는 부분 중

oracle.jdbc.driver.OracleDriver >> oracle.jdbc.OracleDriver

수정하면 해결 됨