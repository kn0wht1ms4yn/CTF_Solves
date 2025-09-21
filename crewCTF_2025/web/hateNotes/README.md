#### Hate Notes
- points earned: 426

#### Notes

- CSP rule `style-src ${HOSTNAME}/static/;` means that we can src css from a url that starts with something like `http://host/static/`

- CSP rule `img-src 'none';` prevents us from using a css rule like `background: url()` but since there's no rule for `font-src` we can still import a font from remote.

- `/static` route contains logic that removes `/static` and redirects to the result.  This allows us to access notes at a url like `http://host/static/api/notes/{note_id}`.
```javascript
app.get('/static/*splat', (req, res) => {
  const requestedPath = req.path; 

  if (!requestedPath.endsWith('.js') && !requestedPath.endsWith('.css')) {
    return res.redirect(requestedPath.replaceAll('/static',''));
  }

  let file = req.path.slice(req.path.lastIndexOf('/')+1)
  const filePath = path.join(__dirname, 'static', file);
  res.sendFile(filePath);
});
```

- Accessing `http://host/static/api/notes/{note_id}` does not return a `Content-Type`, so if the browser thinks its CSS then it can be treated as css.

#### Theory

- Craft a note that is accessible at `http://host/static/api/notes/{note_id}` where the response is a valid css document.

- Craft another note that `<link>`s that CSS.

- The CSS looks for the last `<li>` on a page and loads a font if its href starts with a specific set of characters.

- Send the second note to the bot repeatedly until all characters of the href are retreived.

- Access the note to reveal the flag.
