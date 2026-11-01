# DAS / Roche Lab FAQS — v4 Original Pages Only

Complete offline app, retaining the navy/green liquid-glass styling and chapter/topic navigation.
This release intentionally removes reconstructed handbook text from the user interface.

## The rule in this version

ALL HANDBOOK CONTENT IS DISPLAYED AS ORIGINAL PAGE IMAGES OR THE ORIGINAL PDF.
- No reconstructed text reader or Reading view toggle.
- No OCR/extracted paragraphs, scientific instructions or answer snippets in result cards.
- No retyped tables, reformatted formulas, interpreted symbols or generated answers.
- Search and question results show topic/navigation labels, page references and original-page thumbnails.
- Every topic opens an original source page, with Previous / Next and original-page thumbnails.
- Tap a page to enlarge it; zoom controls and scrolling are available.
- The complete original book viewer includes all 387 pages: covers, front matter, chapter dividers,
  notes, blank pages and publication information. No pages were removed from that viewer.
- handbook.pdf is the unchanged supplied PDF. Its hash is recorded in test-report.json.

All 387 page images were rendered directly from that PDF at scale 2.5 (approximately 1240 pixels wide
for the usual page size) and encoded as LOSSLESS WebP. No cropping, OCR reconstruction, retypesetting,
colour filter or glossy overlay is applied to the source image itself. Glass styling is on its frame.
Pixel comparisons on sample pages 13, 81 and 341 confirmed equality with their fresh PDF renderings.
This is not a claim that every source page has been manually proofread or scientifically validated.

Page images are raster previews at a finite resolution. For very fine detail or vector-quality zoom,
open the original PDF using the button provided. Native PDF viewers may ignore a page-jump link;
use the displayed PDF page number manually. Images cannot offer reflowable/selectable text; the PDF
is included for viewers that support selectable source text and assistive reading. Accessibility
of that PDF's text layer depends on the original document and the viewer, and is not validated here.

## Separate limitation: the search index

Search and question lookup STILL USE THE PDF'S EXTRACTED TEXT INTERNALLY to locate topics/pages.
That hidden index is not a verified transcription and can miss or misread matches, especially for
symbols, tables, names and page-layout artifacts. It is never displayed as a handbook passage or answer.
The app labels this limitation in Search and Find by question. No matches does not prove the handbook
lacks a topic. Browse the source if necessary. A match is not proof of relevance; read the original page.

Chapter/topic labels are navigation metadata derived from source headings, not substitutes for the
actual page. Some labels were corrected for obvious extraction damage; they are not guaranteed to be
a verbatim or manually checked table of contents. Original printed headings remain visible in the page.

Find by question is a keyword/word-variant document finder, not AI. It does not reason, calculate,
translate, interpret images, verify facts or infer previous question context. Each question is independent.

## Structure and features

Chapter -> Topic -> Original source pages. Seven chapters, 175 named topics and 46 source sections.
- Shared topic cards for browsing, search, questions and bookmarks.
- Chapter-specific title filtering and full index search with chapter/exact-phrase filters.
- Original-page thumbnails rather than extracted summaries.
- Topic bookmarks, with earlier page bookmark migration where possible on the same origin.
- Complete original book viewer with a PDF page-number box and Previous / Next controls.
- Lossless image enlargement/zoom and direct original PDF links.
- White/faint-green background, navy #0f2a49 menu, #84bd22 selections/actions.
- Glossy glass UI, sliding menu selection, fluid entrances and reduced-motion support.
- Light, dark and system themes; source images keep their original colours in every theme.
- Offline caching of the application, all 387 images and PDF (approximately 22 MB).

## Computer preview

Extract the ZIP completely. Open index.html for a quick local-file preview.
For representative offline/PWA testing, use the included local server instead.

Requires Python 3 only, without extra packages:
- Windows: double-click START-WINDOWS.bat, or run `python start_server.py`.
- macOS/Linux: run `python3 start_server.py` from the extracted application folder.

The launcher serves this folder only on this computer at http://localhost:8000 and opens the browser.
Keep its terminal open during testing. Ctrl+C stops it. Localhost on your phone is not your computer.

## Phone installation / hosting

The app has not been deployed for you. Publish the web files and complete pages/ directory to a
static HTTPS host, preserving relative paths. No application backend, AI server or database is needed.
Subdirectory hosting is supported. A normal unencrypted LAN HTTP URL is not a substitute for HTTPS
for phone installation. Localhost is a special development exception on the computer itself.

1. Open the HTTPS site while online.
2. Wait for Ready offline. All images and the PDF must finish caching first.
3. iPhone: use Add to Home Screen from the browser's Share menu.
4. Android: use Install app / Add to Home screen in the browser menu.
5. Open the installed app once online, check readiness, then test airplane mode.

First use and updates require connectivity. After caching, original page browsing/zoom, lookup,
bookmarks, all-book paging and PDF access run locally. Clearing website data, private mode or browser
storage eviction can remove the cache/bookmarks. Keep a separate PDF copy for important access.

Deploy these web files: index.html, style.css, app.js, search.js, motion.js, data.js, sw.js,
manifest.webmanifest, all icon files, handbook.pdf, and every file in pages/.
README, launcher files, licence, test report, content-map.csv and previews/ need not be hosted.
Use appropriate MIME types for JavaScript, WebP and the web manifest. Do not cache sw.js indefinitely
on the server. If you edit assets later, change the cache version in sw.js so the full set is refreshed.

## Updating v2/v3

Replace all app files together on the same origin/path. Bookmark storage keys and 175 topic IDs are
preserved, so earlier topic bookmarks are retained where the browser's storage remains available.
The service worker uses a new cache and deletes earlier lab-pocket caches only after installation.
Load online, wait for readiness, close/reopen the app, and confirm the header says Original pages.
An installed app may need its icon/name refreshed by reinstalling; physical OS behaviour is not tested.
Changing domains/paths or clearing storage does not preserve bookmarks automatically.

## Privacy, age and rights

No AI API, external scripts, external fonts, CDN libraries or analytics. Search and questions run on the
device; questions stay in current-session memory only. Bookmarks/themes use localStorage and offline
files use the Cache API. The website host may log initial download/update requests.

Original pages avoid newly introduced transcription errors, but do NOT make the source current or
scientifically correct. The Roche Lab FAQs third edition includes material and website checks from 2007.
Follow current SOPs, manufacturer instructions and safety data. This is an independent reference tool,
not a validated laboratory/clinical decision system or an official/endorsed Roche application.

The supplied PDF, extracted index, navigation/source text and page renderings retain their original
rights. The code licence grants no permission to publish those materials. Obtain any necessary
permission before redistributing them. DAS branding is a requested typographic treatment, not a
supplied official logo or a statement of affiliation.

## Tests

See test-report.json for the unchanged PDF hash, lossless-render sample checks and browser checks.
Automated Chromium tests cover original-page default display; absence of a reconstructed-text mode;
absence of extracted scientific passages in search/questions; source thumbnails; previous/next source
paging; complete book cover and final page; zoom; offline images/PDF; bookmarks across offline reload;
mobile/desktop overflow; dark mode and reduced motion. No JavaScript errors or external requests were
observed. Screenshots are in previews/; content-map.csv documents the topic/source-page associations.

Physical iPhone/Android devices, Safari/WebKit, OS home-screen installation, sustained performance,
complete screen-reader accessibility and manual scientific proofreading remain untested.
