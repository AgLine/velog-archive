# ROW_NUMBER()의 ORDER BY 사용이유

게시일: Mon, 14 Oct 2024 07:53:20 GMT
링크: https://velog.io/@agline/ROWNUMBER%EC%9D%98-ORDER-BY-%EC%82%AC%EC%9A%A9%EC%9D%B4%EC%9C%A0

---

<h1 id="chatgpt기록용"><em>chatGPT기록용</em></h1>
<p><code>ORDER BY ISTREQ.RECEPTION_NUM</code>는 쿼리에서 <code>ROW_NUMBER()</code> 함수를 사용하는 이유와 관련이 있습니다. <code>ROW_NUMBER()</code>는 결과 집합의 각 행에 고유한 일련 번호를 부여하는데, 이 번호는 특정 순서대로 매겨져야 합니다. 이 순서를 지정하지 않으면 결과가 임의로 정렬될 수 있습니다.</p>
<p>다음은 이유를 더 구체적으로 설명한 내용입니다:</p>
<ol>
<li><p><strong>ROW_NUMBER()의 동작</strong>: <code>ROW_NUMBER()</code> 함수는 데이터를 순서대로 정렬하고, 그 정렬 순서에 따라 각 행에 번호를 붙입니다. 이때 어떤 열을 기준으로 순서를 매길지 지정해야만 함수를 올바르게 사용할 수 있습니다. <code>ORDER BY ISTREQ.RECEPTION_NUM</code>는 <code>ISTREQ</code> 테이블의 <code>RECEPTION_NUM</code> 열을 기준으로 정렬하고, 그에 따라 행 번호를 매깁니다.</p>
</li>
<li><p><strong>일관된 페이징</strong>: 쿼리에서는 <code>ROW_NUMBER()</code>로 부여된 행 번호를 이용해 페이징을 수행하고 있습니다. <code>ROW_NO BETWEEN #{startRow} AND #{endRow}</code> 조건을 통해 특정 범위의 행만 선택하는데, <code>ORDER BY</code>를 지정하지 않으면 페이징된 데이터의 순서가 불규칙해지거나 각 페이지에서 중복된 데이터가 나타날 수 있습니다. 즉, <code>RECEPTION_NUM</code>으로 일관된 순서를 보장함으로써 페이지를 넘길 때마다 같은 순서로 데이터가 잘라져 나옵니다.</p>
</li>
</ol>
<p>따라서 <code>ORDER BY ISTREQ.RECEPTION_NUM</code>은 쿼리에서 <code>ROW_NUMBER()</code>의 기능을 올바르게 동작하게 하고, 안정적인 페이징 처리를 위해 반드시 필요합니다.</p>
<p>네, <code>RECEPTION_NUM</code> 대신 다른 컬럼으로도 정렬할 수 있습니다. 중요한 것은 <code>ROW_NUMBER()</code> 함수가 적용될 때 어떤 컬럼을 기준으로 정렬할지 명확하게 지정하는 것이기 때문에, 페이징 및 원하는 결과에 맞는 컬럼으로 정렬을 설정하면 됩니다.</p>
<p>다만, 다른 컬럼을 선택할 때 주의할 점은 다음과 같습니다:</p>
<ol>
<li><p><strong>페이징의 일관성</strong>: 페이징을 구현하는 것이 목표라면, 선택한 정렬 기준이 데이터의 일관성을 유지할 수 있는 컬럼이어야 합니다. 예를 들어, <code>RECEPTION_NUM</code> 대신 <code>IST_REQ_VISIT_DATE</code>나 <code>CLIENT_NAME</code> 같은 컬럼을 사용할 수 있지만, 정렬된 결과가 변경될 수 있는 컬럼이라면 페이징이 불안정해질 수 있습니다(예: 값이 중복되거나 변경되는 경우).</p>
</li>
<li><p><strong>데이터의 고유성</strong>: <code>ROW_NUMBER()</code>는 고유한 번호를 부여하기 때문에, 선택한 컬럼이 중복값을 많이 포함하는 경우에는 페이징 결과가 예기치 않게 나올 수 있습니다. 예를 들어, <code>CLIENT_NAME</code>으로 정렬할 경우 이름이 같은 여러 행이 있을 수 있으므로, 순서가 임의로 섞일 수 있습니다. 이 경우 추가적으로 보조 정렬 기준을 넣어 고유성을 확보하는 것이 좋습니다(예: <code>ORDER BY CLIENT_NAME, RECEPTION_NUM</code>).</p>
</li>
<li><p><strong>비즈니스 로직</strong>: 정렬 기준이 비즈니스 요구 사항에 맞아야 합니다. 데이터를 조회하는 목적에 따라 중요한 순서가 달라질 수 있습니다. 예를 들어, 가장 최근의 방문 요청을 먼저 보고 싶다면 <code>IST_REQ_VISIT_DATE</code>로 정렬하는 것이 적절할 수 있습니다.</p>
</li>
</ol>
<p>요약하자면, <code>RECEPTION_NUM</code> 외에도 다른 컬럼으로 정렬할 수 있지만, 페이징의 일관성과 데이터의 고유성을 고려하여 적절한 컬럼을 선택하는 것이 중요합니다.</p>