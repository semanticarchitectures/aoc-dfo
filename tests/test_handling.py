"""NFR-3, R12.5: no handling markings copied into the public repo."""

from aoc_dfo.handling import PATTERNS, scan


def test_repo_has_no_handling_markings():
    assert scan() == []


def test_patterns_catch_markings_but_not_prose():
    banner = "\nSECRET//NOFORN\n"
    portion = "(CUI) The ATO is"
    prose = "HANDLING.md says CUI and NOFORN material must never be committed."
    inline = "see the S//REL TO USA, FVEY header"
    assert PATTERNS["banner marking"].search(banner)
    assert PATTERNS["portion marking"].search(portion)
    assert PATTERNS["dissemination control"].search(inline)
    assert PATTERNS["portion marking"].search('mo:X,"(S) The tasking is')  # start of a CSV field
    # NIEM prose that mentions a letter or CUI in parentheses is not a marking
    for text in ("A single character (C) alphabetic prefix.",
                 "A controlled unclassified information (CUI) handling restriction."):
        assert not any(p.search(text) for p in PATTERNS.values()), text
    assert not any(p.search(prose) for p in PATTERNS.values())
