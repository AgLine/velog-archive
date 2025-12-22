# HttpServletRequest로 POST Body RequestData 조회

게시일: 2024-08-13T05:54:20.136Z
시리즈: No-Series

---


```
@ResponseBody
@PostMapping("/ajaxReq")
public Map<String, Object> ajaxReq(HttpServletRequest request){

	Map<String, Object> resultMap = new HashMap<>();
	AjaxVO ajaxVO = new AjaxVO();

	ajaxVO.setVarOne(request.getParameter("varOne"));
	System.out.println(ajaxVO.getVarOne());
	return resultMap;
}
```
늘 하던방법대로 했지만 null이 출력됨

```
@ResponseBody
@PostMapping("/ajaxReq")
public Map<String, Object> ajaxReq(HttpServletRequest request)throws ServletException, IOException{
	Map<String, Object> resultMap = new HashMap<>();
    
    ServletInputStream inputStream = request.getInputStream();
    String data = StreamUtils.copyToString(inputStream, StandardCharsets.UTF_8);
    
    System.out.println("message body = " + data);
    
    return resultMap;
}
```
이후 정상적으로 요청값을 받았음

# Reference
https://velog.io/@gorapaduckoo/HttpServletRequest%EB%A1%9C-%EC%9A%94%EC%B2%AD-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%A1%B0%ED%9A%8C%ED%95%98%EA%B8%B0