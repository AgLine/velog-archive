# Oracle날짜 기간 조회 +0.99999를 하는이유

게시일: Mon, 14 Oct 2024 07:50:58 GMT
링크: https://velog.io/@agline/%EB%82%A0%EC%A7%9C-%EA%B8%B0%EA%B0%84-%EC%A1%B0%ED%9A%8C

---

<p>날짜 기간을 조회하는 방법을 검색하던 도중 궁금증이 생김</p>
<h3 id="문제-설명">문제 설명:</h3>
<ul>
<li><code>TO_DATE('20241014', 'YYYYMMDD')</code>은 <code>2024-10-14 00:00:00</code>를 반환 </li>
<li>Oracle에서 <strong>날짜(<code>DATE</code>) 데이터 타입</strong>은 기본적으로 날짜와 시간을 모두 포함하지만, <code>TO_DATE</code> 함수를 사용하면 시간은 <strong>기본적으로 <code>00:00:00</code></strong>으로 설정되기 때문</li>
<li><code>BETWEEN</code> 조건은 <code>&gt;=</code>와 <code>&lt;=</code>의 범위를 가지므로, 실제로는 <code>2014-10-14 00:00:00</code>까지 포함하는 것이지, <code>2014-10-14 23:59:59</code>까지의 시간을 포함하지 않음</li>
<li>그래서 <code>14일</code>의 <strong>하루 전체</strong> 데이터를 조회하려면, 시간을 <strong>23:59:59</strong>로 만들어야 함</li>
</ul>
<h3 id="099999의-의미"><code>0.99999</code>의 의미:</h3>
<p>Oracle에서 날짜 데이터는 소수점으로 <strong>시간</strong>을 표현할 수 있음</p>
<ul>
<li><code>1</code>일은 24시간이므로, <code>0.5</code>는 12시간을 의미</li>
<li><code>0.99999</code>는 거의 <strong>하루의 끝</strong>을 의미하며, 이는 <code>23:59:59</code>에 근접한 시간입니다.</li>
</ul>
<p>따라서, <code>TO_DATE('20241014', 'YYYYMMDD') + 0.99999</code>는:</p>
<ul>
<li><code>2014-10-14 23:59:59</code>과 같은 의미로 동작하여, <strong>14일의 마지막 순간까지</strong> 데이터를 포함시킬 수 있음</li>
</ul>
<h3 id="결론">결론:</h3>
<ul>
<li><code>TO_DATE(#{date2}, 'YYYYMMDD')</code>는 기본적으로 <code>00:00:00</code>이므로 하루의 첫 번째 순간까지만 포함하게됨</li>
<li><code>+ 0.99999</code>를 하면 해당 날짜의 <strong>마지막 시간(23:59:59)</strong>까지 포함할 수 있음</li>
</ul>