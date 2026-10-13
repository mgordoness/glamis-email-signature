# Glamis Dunes Rentals email signatures

Images for the Glamis Dunes Rentals email signatures used in Front.

The whole signature card is drawn as images, because dark mode in email apps
(Front, Gmail, Outlook, Apple Mail) recolors HTML backgrounds and text but
leaves images alone. The card is cut into slices so the phone, email and
website lines each keep their own link.

- `common/` - slices shared by everyone: logo block (Glamis + BRP Experiences), phone line, website line, bottom spacer, "Start your adventure" bar.
- `people/<name>/` - each person's name slice, email slice and `signature.html` (paste into Front in HTML mode).
- `glamis-brp-signature-logo.png` - the combined Glamis + BRP Experiences logo used in the logo block.
- `tools/make_card.py` - builds the slices and HTML.

Add a teammate:

```
python3 tools/make_card.py --name "First Last" --email first@glamisrent.com
```

Don't rename, move or delete files here: live email signatures load them from this repo's raw URLs.
