#### S3cret5
- points earned: 0 :(
- Note: Although I was able to solve this problem locally, I was not able to solve on the remote challenge.  Details below.

#### Weaknesses: `CSPT` in `/user/profile/?id=2`
```js
// profile.ejs
const profileIds = urlParams.getAll("id");
const profileId = profileIds[profileIds.length - 1]; 


fetch("/log/"+profileId, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
        userId: "<%= user.id %>", 
        action: "Visited user profile with id=" + profileId,
        _csrf: csrfToken
    })
})
```
- The problem here is that `id` gets added onto `/log/` in the fetch which means that if `id=../meow` then it will end up sending a fetch to `/log/../meow`.
- Also take note of the logic on `profileId`.  It takes the last `id` param in the url.
```js
// userController.js
const userId = parseInt(req.query.id);
```
- When a user navigates to `/user/profile?id=1` then the logic ends up taking the first occurrence of the `id` paramter in the url. This is important because it is used as the value `<%= user.id %>` in `profile.ejs`.
- In this case, if the admin goes to `/user/profile?id=<userId>&id=../admin/addAdmin` then it will trigger the CSPT and a POST request will be sent to `/admin/addAdmin` with the `userId` parameter set to whatever was provided as the FIRST `id` parameter.
- This can be used to escalate permissions on our user by getting them asigned the admin role.

#### Weakness: SQLi
- Any user with the `admin` role can access `/admin/msgs`.
```js
// Msg.js
findAll: async (filterField = null, keyword = null) => {
    const { clause, params } = filterHelper("msgs", filterField, keyword);
    const query = `
      SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username
      FROM msgs
      INNER JOIN users ON msgs.userId = users.id
      ${clause || ""}
      ORDER BY msgs.createdAt DESC
    `;
    const res = await db.query(query, params || []);
    return res.rows;
  },
```
```js
// filterHelper.js
function filterBy(table, filterBy, keyword, paramIndexStart = 1) {
  if (!filterBy || !keyword) {
    return { clause: "", params: [] };
  }

  const clause = ` WHERE ${table}."${filterBy}" LIKE $${paramIndexStart}`;
  const params = [`%${keyword}%`];

  return { clause, params };
}
```
- When the user filters the messages, they send `filterBy` and `keyword` to `/admin/msgs` and a query is created in the `findAll` function with some help of the `filterBy` function.
- The `filterBy` function DOES NOT parameterize the `filterBy` value which means that an sql injection can occur.
- The resulting query will look like this `SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username FROM msgs INNER JOIN users ON msgs.userId=users.id WHERE msgs."msg" LIKE "%meow%" ORDER BY msgs.createdAt DESC`
- Since we can inject into the `filterBy` parameter then we can make it look like this `SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username FROM msgs INNER JOIN users ON msgs.userId=users.id WHERE msgs."msg" LIKE '%meow%' and (select ascii(substring(flag from {pos} for 1)) & {bits} from flags)={bits} and msgs."msg" LIKE "%meow%" ORDER BY msgs.createdAt DESC`.
- One interesting thing to note is that I was unable to use the common approach of adding `--` after my injection point.  Instead, I had to make a complete valid string.  I believe this was due to the fact that the query contains multiple lines and the comment only applies to the line that its on.
- This part I scripted out in `get_flag.py`.

#### Why I was unable to solve the remote challenge
- There was a header(`SRV`) that I should have been using that was not scripted into my solution.
- It was very strange because the challenge app continued to respond to my requests as if there was nothing wrong, but the sqli was returning garbage.
- My understanding is that the `SRV` header was used for load balancing on the remote app.
- :/

#### Solution
- Create an account and take note of the `userId` which is included in the login response(and other places).
- Escalate the new user to admin by triggering the bot to navigate to go to `http://me:3000/user/profile?id=<userId>&id=../admin/addAdmin`.
- Exploit boolean based blind sqli in `/admin/messages` `filterBy` parameter.
