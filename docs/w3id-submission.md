# Submitting the w3id.org request

**Status:** merged; checked end to end 2026-11-11 (`/ontology`, `/aoc-flows`, `/0.1.0/…`, `.ttl` and the
root all redirect as designed and land on `200 text/turtle` or `text/html`).
Submitted 2026-11-08 as [perma-id/w3id.org#7107](https://github.com/perma-id/w3id.org/pull/7107),
from `semanticarchitectures/w3id.org` branch `aoc-dfo` (commit `705d161`). The Pages target was checked
live first (`200 text/turtle`). Keep `docs/w3id/` identical to what is merged.

The identifier `https://w3id.org/aoc-dfo/` is drafted in [`docs/w3id/`](w3id/): `.htaccess` and
`README.md`, the only two files w3id allows in an identifier directory. Checked 2026-10-24:

- the name `aoc-dfo` is free in `perma-id/w3id.org` (`ids/`, master at `a71f3bd`);
- the draft passes w3id's own checker (`tools/check`, 42 rules, no findings);
- every rule was exercised on Apache 2.4.58: 15 requests redirect where intended (browser → HTML,
  everything else → Turtle, versioned and explicit `.ttl` forms) and 4 malformed paths return 404.

w3id reviewers check that the redirect target is **already live over HTTPS**, so publish first.

## 1. Publish the target (GitHub Pages)

1. In this repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Re-run the **Pages** workflow (Actions → Pages → Run workflow), or push to `main`.
3. Check the documents are live and typed as Turtle:

   ```sh
   curl -sI https://semanticarchitectures.github.io/aoc-dfo/ontology.ttl | grep -iE '^(HTTP|content-type)'
   curl -sI https://semanticarchitectures.github.io/aoc-dfo/0.1.0/aoc-flows.ttl | grep -iE '^(HTTP|content-type)'
   ```

   Expect `200` and `content-type: text/turtle`. If Pages serves `text/plain`, stop and say so: the
   redirect works but RDF clients will mis-parse, and the target needs to change before submitting.

## 2. Open the pull request

1. Fork [perma-id/w3id.org](https://github.com/perma-id/w3id.org) and sync it with `master`.
2. Copy `docs/w3id/.htaccess` and `docs/w3id/README.md` to `ids/aoc-dfo/` in the fork. In the
   GitHub web editor, type the whole path `ids/aoc-dfo/.htaccess` into the filename box, or the
   leading dot is refused.
3. One commit, with this message. It deliberately has **no agent-session link**: w3id's rule
   `git/no-session-link` flags those.

   ```
   aoc-dfo: add persistent IRIs for the AOC Data Flow Ontology

   Content-negotiated IRIs for AOC-DFO, a BFO/CCO ontology of USAF Air
   Operations Center data flows built from public sources. Browsers get
   the HTML landing page; other clients get Turtle. Versioned documents
   live under <x.y.z>/. Target: https://semanticarchitectures.github.io/aoc-dfo/
   ```

4. Pull request title: `aoc-dfo: add persistent IRIs for the AOC Data Flow Ontology`. Body:

   ```markdown
   Adds `https://w3id.org/aoc-dfo/` for AOC-DFO, an open (Apache 2.0) BFO/CCO ontology of USAF
   Air Operations Center data flows built only from public sources.
   Source: https://github.com/semanticarchitectures/aoc-dfo

   | IRI | Redirects to |
   | --- | --- |
   | `/aoc-dfo/` | landing page (302) |
   | `/aoc-dfo/ontology` (namespace `…/ontology#`) | HTML for browsers, else `ontology.ttl` (303) |
   | `/aoc-dfo/aoc-<module>` | HTML for browsers, else `<module>.ttl` (303) |
   | `/aoc-dfo/<x.y.z>/<doc>` | the same, at a release (303) |
   | `/aoc-dfo/<doc>.ttl`, `/aoc-dfo/<x.y.z>/<doc>.ttl` | the Turtle file (302) |

   The target is live on GitHub Pages over HTTPS. Checked with `tools/check` (no findings) and
   against a local Apache 2.4 with browser, Turtle, `*/*` and RDF/XML-first `Accept` headers.

   Maintainer: Kevin G. Kelly, GitHub @semanticarchitectures.
   ```

## 3. After merge

```sh
curl -sIL -H 'Accept: text/turtle' https://w3id.org/aoc-dfo/ontology | grep -iE '^(HTTP|location|content-type)'
curl -sIL https://w3id.org/aoc-dfo/ | grep -iE '^(HTTP|location)'
```

Changes later (new hosting, new document types) are a PR to `ids/aoc-dfo/` only. Keep
`docs/w3id/` here identical to what is merged there.
