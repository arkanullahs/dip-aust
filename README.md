# DIP for AUST

A complete, plain-words tutorial for **CSE 4227 Digital Image Processing** at AUST.

**Site:** https://arkanullahs.github.io/dip-aust/

- **Lessons**: one page per slide deck (decks 01–14). Each explains every slide in plain words with real graphs, solves the past final and quiz questions in answer-script form, and has step-by-step simulators wherever a method appears (histogram equalization, filters, Canny, region growing, chain code, morphology, Huffman, LZW, arithmetic coding, Golomb, RLE, RMSE, colour conversion …).
- **Revision**: the ultimate page (every past question as the paper image, next to its worked answer), a mega formula sheet, a segmentation fast track, the Fall 2025 quiz answers, and a questions-only page for self-testing.
- **Trainers**: region growing, LZW and chain code, practised the way you do them on paper.

Questions marked ★ in the lessons are the ones that come back paper after paper (Spring 2022 – Spring 2025 finals and the Fall 2025 quizzes).

## Layout

```
build.py              builds the whole site into _site/ (stdlib Python 3.10+, nothing to install)
src/
  kit.py              shared HTML helpers: page, paper boxes, tables, matrices, SVG plots and bars
  sim_kit.js          every step-by-step simulator (one engine, many types)
  sim_kit_test.js     maths checks for the simulators:  node src/sim_kit_test.js
  dNN/buildNN.py      one generator per slide deck; writes dNN/deckNN_lesson.html
  must.py             adds the ★ must-study marks to the built deck pages
  mega/               revision pages; they lift paper boxes and simulators from the built decks
  trainers/           stand-alone trainer pages
  static/             pages copied as they are
data/                 past questions (text, marks, topic tags) used by the revision pages
crops/                question images cut from the past papers
.github/workflows/    rebuilds and deploys the site on every push to main
```

Every number shown on a page is computed in its generator, and most generators `assert` the
results, so a page cannot disagree with its own maths.

## Build and preview

```
python build.py
python -m http.server -d _site 8000
```

Then open http://localhost:8000. `python build.py --no-generate` re-assembles the site without re-running the generators.

## Fix or add something

- **A mistake in a lesson**: edit `src/dNN/buildNN.py`, rebuild, check the page, and open a pull request.
- **A new lesson or revision page**: write its generator (copy a deck build as a starting point and use `kit.py`), then add one line to `LESSONS`, `REVISION` or `TRAINERS` at the top of `build.py`. The home page and the navigation pick it up from there.
- **A new simulator type**: add it to `src/sim_kit.js`, register it in the dispatch table at the bottom, and add a check to `sim_kit_test.js`.
- **New past questions**: add them to `data/`, put the cropped image in `crops/`, and tag the question in `data/tags.json`.

The site is built and deployed by GitHub Actions when a change lands on `main`, so nothing generated is committed.

## Notes

- The course slides themselves are not in this repository; the lessons follow their slide numbers.
- Written for the Fall 2025 offering (Prof. Dr. Kazi A Kalpoma). Hough transform and the frequency domain were outside that syllabus.
