# mybatis bad SQL grammar []] with root cause

게시일: 2024-07-29T12:03:05.483Z
시리즈: DataBase

---

sql문만 돌리면 잘 작동하는데 mybatis에서 자꾸 문법이 잘못되었다고 뜸

```
SELECT * 
  FROM EXAMPLE;
```
끝에 세미콜론 찍으면 안됨

```
SELECT * 
  FROM EXAMPLE
```

지우고 다시 실행하면 정상적으로 작동