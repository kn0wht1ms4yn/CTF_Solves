#### Shell
- points earned: 50

#### Where's the flag?
- no src code provided so we have to just go looking for it.
#### Notes / Intuition
- Just getting a feel for the app, I uploaded a sample image and got the response below.
	```bash
	ExifTool Version Number         : 12.16
	File Name                       : marvin.png
	Directory                       : static/uploads
	File Size                       : 4.8 KiB
	File Modification Date/Time     : 2026:02:15 18:14:41+00:00
	File Access Date/Time           : 2026:02:15 18:14:41+00:00
	File Inode Change Date/Time     : 2026:02:15 18:14:41+00:00
	File Permissions                : rw-r--r--
	File Type                       : PNG
	File Type Extension             : png
	MIME Type                       : image/png
	Image Width                     : 157
	Image Height                    : 148
	Bit Depth                       : 8
	Color Type                      : Palette
	Compression                     : Deflate/Inflate
	Filter                          : Adaptive
	Interlace                       : Noninterlaced
	Palette                         : (Binary data 396 bytes, use -b option to extract)
	Image Size                      : 157x148
	Megapixels                      : 0.023
	```
	- This looks like bash output from the `exiftool` command
- I took a couple whacks here trying command injection without any luck
- I researched `exiftool` and found the current version to be `13.50`
- I then search for exiftool vulns with a search like `exiftool vulns`
- Found `cve-2021-22204`
	- Improper neutralization of user data in the DjVu file format in ExifTool versions 7.44 and up allows arbitrary code execution when parsing the malicious image
- I then went looking for a POC for this and found
	- https://github.com/UNICORDev/exploit-CVE-2021-22204

#### Solution
- Use the POC to read  the flag
