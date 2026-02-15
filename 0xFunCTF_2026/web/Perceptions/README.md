#### Perceptions
- points earned: 50

#### Where's the flag?
- no source code was provided with this challenge so we have to go looking for it.
#### Notes / Intuition
	- The app text indicates I can connect to multiple services via the same port, on the My Server page
	```
	It used to have a few ports open to run different things but now that I have Perceptions I only need one port for everything which is pretty cool
	```
- Comments in the client-side source code leak a password.
	```
	Thought I'd make things a bit fun and hide a password on this page. When I get the login page working it will let you see some extra posts...
	        <!-- Use my name and 'UlLOPNeEak9rFfmL' to log in -->
	```
- On the proxy, I noticed a request `/name` that replies `charlie`.
- trying to connect via telnet I get
	```bash
	kno@kBox ~$ telnet -l charlie chall.0xfun.org 48950                                                                                                                                 
	Trying 54.252.250.249...  
	Connected to chall.0xfun.org.  
	Escape character is '^]'.  
	asdasd  
	Detected protocol 'UNKNOWN', Perceptions cannot serve this protocol. Supported: HTTP, SSH  
	Connection closed by foreign host.
	```

#### Solution
- connect to the box via ssh with credentials `charlie:UlLOPNeEak9rFfmL`
	```bash
	kno@kBox ~$ ssh charlie@chall.0xfun.org -p 48950                                                                                                                                    
	(charlie@chall.0xfun.org) Password:  
	=== CHARLIE'S FUN ZONE!!! ===  
	This is my custom shell, there's not much in it right now, but remember how to navigate a terminal and you'll be fine! :>  
	```
- read files in current dir as stanadard enumeration
	```bash
	/ $ ls  
	README.txt  
	secret_flag_333  
	4C6Y4NEBVLATCF6EX5PA2ISZ  
	6PP5RVOYV54Z7DUASYLKF2FK  
	style.css  
	MHEGSBREXSEDFLXPWXVAA2GQ  
	img  
	25YDY4737K3QMIZ6N5OUEYGL  
	login.html  
	3XSPO7ZJP27IUGMANNB2V2J3  
	links.js
	```
- read `secret_flag_333`
	```bash
	/ $ cat secret_flag_333  
	Error: That's a folder! :(
	```
- Oops, thats a dir so cd and list
	```bash
	$ cd secret_flag_333    
	  
	/secret_flag_333 $ ls  
	flag.txt
	```
- read flag.txt
	```bash
	/secret_flag_333 $ cat flag.txt  
	  
	  Welcome to my backend! Should you be here?  
	  
	           ▄▄█████▄                                               
	            ▄███▄▄                                                
	           ▀▄▄  ▄▄▀                                               
	           ▀▄▄▀█▄▄▀                                               
	            ▀████▀                                                
	          ▀██▀  ▀██▄                                              
	          ▄▀▀ ▀▀ ▀▀▄                                              
	            ▄    ▄                                                
	                                                                  
	            ▀▀▀▀▀▀                                                
	         ▀▄█   ▀▄  ▀▀                                             
	          ▄▀      ▀▄                                              
	         ▄▀      ▀ ▄▄                   ▄▄▄▄▄                     
	         ▀▀▀▀▀▀▀▀▀▀▀▀                  ▀▀▀▀▀▀▀                    
	               ▀█                    ▀▀▄▄▄▄▄▄▄█▄                  
	           ▄▄▄▀▀▄▄▄                        ▀ ▀▀                   
	                                            ▄█▄▄▄                 
	                             ▄▀▀▄▄▄▀▀▀      ▀▀▀▀▀                 
	                              ▀████████████████                   
	 0xfun{p3rsp3c71v3.15.k3y}     ▀████▄▀▀▀▀▄████▄▀                  
	                               ▀▄▀▀█████████▀▄▀                   
	                                 ▀▀▄▄▄▄▄▄▄▄▄▀
	```