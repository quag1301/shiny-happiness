# Thumbnail maker

Makes 1280×720 "fate card" thumbnails from a JSON list of cards.

1. Put photos (`.jpg`) in `photos/`. The name of each file (without `.jpg`) is what you use for `"photo"`.
   Good free source: the Wikipedia/Wikimedia Commons photo of the person. Note the license and credit it in the video description.
2. Edit `thumbs.json`. Each thumbnail has a `file` name and 4 `cards`. Card fields:
   - `name`, `why` (short reason), `icon` (emoji), `big` (the big number), `unit` (small text under it)
   - `photo` (file in photos/), or `brand` `{text,bg,fg,size}` for a logo-style text card. With neither, you get a silhouette.
   - optional: `badge` (bottom-left of photo), `tag` (bottom-right), `bar` (name bar color), `numc` (number color),
     `chip` `["+31%","#16a34a"]` (top-right label), `stamp` ("BANKRUPT"), `silmark` ("?" on silhouette), `hl` (yellow highlight)
3. Build it (needs Python 3 and Node with Playwright):

```bash
mkdir -p build out && python3 make_thumbs.py photos build thumbs.json && node render.js "$PWD/build" "$PWD/out"
```
