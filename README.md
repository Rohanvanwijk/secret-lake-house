# Secret Lake House Website

This is the Boutique design converted into editable website pages.

## Edit the site

- Change page text in the `.html` files.
- Change colors, spacing, and layout in `styles.css`.
- Change booking-widget behavior in `script.js`.
- Change the Secret Lake House Admin chatbot knowledge in `slh_admin_bot.py`.
- Images currently load from the existing Secret Lake House WordPress uploads.

## Preview locally

Run:

```bash
python serve.py
```

Then open:

```text
http://127.0.0.1:8091/
```

The local preview server also provides the chatbot API at `/api/chat`. If the website is hosted as static files without Python, the chat widget will still answer basic questions with the browser fallback in `script.js`.
