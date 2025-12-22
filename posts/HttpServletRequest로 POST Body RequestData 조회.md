# HttpServletRequest로 POST Body RequestData 조회

게시일: Tue, 13 Aug 2024 05:54:20 GMT
링크: https://velog.io/@agline/HttpServletRequest%EB%A1%9C-RequestData-%EC%A1%B0%ED%9A%8C

---

<pre><code>@ResponseBody
@PostMapping(&quot;/ajaxReq&quot;)
public Map&lt;String, Object&gt; ajaxReq(HttpServletRequest request){

    Map&lt;String, Object&gt; resultMap = new HashMap&lt;&gt;();
    AjaxVO ajaxVO = new AjaxVO();

    ajaxVO.setVarOne(request.getParameter(&quot;varOne&quot;));
    System.out.println(ajaxVO.getVarOne());
    return resultMap;
}</code></pre><p>늘 하던방법대로 했지만 null이 출력됨</p>
<pre><code>@ResponseBody
@PostMapping(&quot;/ajaxReq&quot;)
public Map&lt;String, Object&gt; ajaxReq(HttpServletRequest request)throws ServletException, IOException{
    Map&lt;String, Object&gt; resultMap = new HashMap&lt;&gt;();

    ServletInputStream inputStream = request.getInputStream();
    String data = StreamUtils.copyToString(inputStream, StandardCharsets.UTF_8);

    System.out.println(&quot;message body = &quot; + data);

    return resultMap;
}</code></pre><p>이후 정상적으로 요청값을 받았음</p>
<h1 id="reference">Reference</h1>
<p><a href="https://velog.io/@gorapaduckoo/HttpServletRequest%EB%A1%9C-%EC%9A%94%EC%B2%AD-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%A1%B0%ED%9A%8C%ED%95%98%EA%B8%B0">https://velog.io/@gorapaduckoo/HttpServletRequest%EB%A1%9C-%EC%9A%94%EC%B2%AD-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%A1%B0%ED%9A%8C%ED%95%98%EA%B8%B0</a></p>