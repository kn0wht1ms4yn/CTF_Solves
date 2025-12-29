#### on error resume next
- points earned: 

#### Notes / Intuition

- Per the db schema, the `users.id` field is defined as a `SERIAL` type.
- Mariadb `SERIAL` type is an `UNSIGNED BIGINT` which is an 8 byte unsigned integer.
- The following line does not return the expected id.  `LastInsertId()` will return an `int64` which means that the original id `9223372036854775807` overflows by 1 and the returned id will be `-9223372036854775808`.
	```go
	id, _ := res.LastInsertId()
	```
- Since valid `users.id` values can only be positive integers, the following insert will fail.
	```go
	db.Exec("INSERT INTO transactions (subject, amount, sender, receiver) VALUES (?, ?, ?, ?)", "Gift from the system", 10, 1, id)
	```
- Apparently Golang makes a habit of not allowing errors, like failed db insert, to break the code.  It quietly continues chugging along.
- In the following line, go tries to convert `user.ID` to an int64 but fails to do so.  The result is that the `users[i].id` for that user  becomes 0.
	```go
	rows.Scan(&user.Name, &user.ID)
	```
- If you edit the code here to print the error you can see `Scan error: sql: Scan error on column index 1, name "id": converting driver.Value type uint64 ("9223372036854775808") to a int64: value out of range`.
- When a user submits a transaction, there is not validation on the receiver and the receiver Id just gets put directly into the insert(below).
	```go
	db.Exec("INSERT INTO transactions (receiver, sender, subject, amount) VALUES (?, ?, ?, ?)", r.Form.Get("receiver"), sender, r.Form.Get("subject"), amount)
	```
- Inside the `Sum()` block there is another `Scan` that fails.  In the `Scan` shown below, the result is that `transactions.Amount` gets the correct amount but a failure occurs when trying to get `transactions.Receiver`.  The result is that both the receiver and the sender get set to `0`.
	```go
	rows.Scan(&transactions.Amount, &transactions.Receiver, &transactions.Sender)
	```
- If we use the transactions table below as an example, when `userID=1` calls `Sum(1)`, the sender and receiver are both 0 and since `userID=2` does not equal the sender ID which would be 0, the transaction does not count towards `userID=2`'s balance.  However, the transaction does show for `userID=0`'s balance.  The result is that, according to `Sum()` `userID=2` still has a balance of `10` AND `userID=0` also has a balance of `10`.  There's an extra 10.
```sql
mysql> SELECT amount, receiver, sender FROM transactions;  
+--------+---------------------+--------+  
| amount | receiver            | sender |  
+--------+---------------------+--------+  
|     10 |                   2 |      1 |  
|     10 |                   3 |      1 |  
|     10 |                   4 |      1 |  
|     10 |                   5 |      1 |  
|     10 | 9223372036854775808 |      2 |  
+--------+---------------------+--------+
```
- To solve the challenge we can basically just keep submitting these transactions until the balance becomes greater than or equal to 1337.
#### Solution
- To speed up the solution first create 4 users A, B, C, and D.
- Transfer 10 from users B, C, and D to user A so user a had a balance of 40.  This allows us to send larger transactions.
- Create a user E with id `9223372036854775808`
- Do repeated transactions from user A to user E until the balance becomes greater than 1337.
- Send a request to `/flag` for `userID=0` and the flag is returned in the response.