"""Cut a source sentence down to a slide-sized phrase.

The rule the handoff sets is "أقل كلمات. أعلى فهم" - fewest words, most
understanding - and the Master Guidelines forbid a paragraph on a slide at all.
But shortening is where a lecture tool quietly starts lying: truncate at a word
count and "risk management is not a substitute for security testing" becomes
"risk management is", which asserts the opposite of the source.

So nothing here shortens by cutting mid-clause. A phrase is either a complete
clause that already fits, or the head clause of a longer sentence, or the
sentence is left alone and the caller keeps it off the diagram. What is dropped
is scaffolding a reader supplies for free - "it is important to note that",
"in this section we" - never the predicate that carries the claim.
"""

from __future__ import annotations

import re

# Openers that carry no information: the sentence means the same without them.
_FILLER = re.compile(
    r"^(?:"
    r"in (?:this|the) (?:section|chapter|lecture|case)(?:,)?\s*(?:i|we|you)?\s*"
    r"|it is (?:important|essential|useful|worth) (?:to note |noting )?that\s*"
    r"|(?:i|we) (?:have )?(?:will |now )?(?:discuss|introduce|focus on|concentrate on|explain)(?:ed)?\s*"
    r"|(?:as|when) (?:i|we|you) (?:have )?(?:discussed|explained|saw|see)(?:,)?\s*"
    r"|there (?:are|is)\s+"
    r"|the objective of this chapter is to\s*"
    r"|generally(?:,)?\s*|essentially(?:,)?\s*|basically(?:,)?\s*|however(?:,)?\s*"
    r")",
    re.I,
)

# A clause boundary a reader already hears as a stop. Splitting here keeps the
# subject and its verb together; splitting on a comma often does not.
_CLAUSE = re.compile(r"\s*(?:[;:]|\s+-\s+|\s+—\s+|(?<=[a-z])\.\s+)")

_TRAILING = " ,;:.-–—"


def _words(text: str) -> list[str]:
    return re.sub(r"\s+", " ", str(text or "")).strip().split()


# A clause opening with one of these is subordinate: "If an inappropriate
# architecture is used" has a verb but no claim, and on a slide it reads as a
# sentence someone forgot to finish.
_SUBORDINATE = re.compile(
    r"^(?:if|when|unless|because|although|though|while|whereas|since|"
    r"as|after|before|until|whether|that|which|who)\b", re.I,
)


# Pedagogy is written as instructions to the learner - "Name the responsible
# role...", "Identify the consequence..." - and an imperative carries no
# auxiliary verb. Without these the whole class was rejected, which is why unit
# 12 dropped its accountability line and unit 14 surfaced the trailing caveat
# "do not invent psychology claims" instead of the teaching clause before it.
_IMPERATIVE = re.compile(
    r"^(?:name|describe|say|identify|state|give|list|trace|apply|compare|"
    r"explain|define|choose|change|redesign|resolve|write|commit|defend|mark|"
    r"cite|predict|derive|evaluate|justify|check|show|find|measure|rank|"
    r"select|solve|sketch|draw|record|report)\b", re.I,
)


def _has_predicate(phrase: str) -> bool:
    """A label is a noun phrase; a claim needs a verb. Reject half-claims."""
    text = phrase.strip()
    if _SUBORDINATE.match(text):
        return False
    if _IMPERATIVE.match(text):
        return True
    return bool(re.search(
        r"\b(?:is|are|was|were|has|have|can|must|should|may|will|does|do|"
        r"requires?|needs?|uses?|provides?|prevents?|protects?|assesses?|"
        r"depends?|means?|becomes?|remains?|fails?|allows?|limits?)\b",
        phrase, re.I,
    ))


def phrase(text: str, limit: int = 9) -> str:
    """Return a complete phrase of at most `limit` words, or "" if impossible.

    An empty return is a real answer: it tells the caller this sentence cannot
    be honestly shortened, so it belongs in the notes rather than on a node.
    """
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    cleaned = _FILLER.sub("", cleaned).strip(_TRAILING)
    if not cleaned:
        return ""
    if len(_words(cleaned)) <= limit:
        # A short sentence still has to be a claim. "If an inappropriate
        # architecture is used" is six words and reads on a slide as a thought
        # someone forgot to finish, so brevity alone does not earn the canvas.
        if not _has_predicate(cleaned):
            return ""
        return cleaned[:1].upper() + cleaned[1:]

    for candidate in _CLAUSE.split(cleaned):
        candidate = candidate.strip(_TRAILING)
        count = len(_words(candidate))
        if 2 <= count <= limit and _has_predicate(candidate):
            return candidate[:1].upper() + candidate[1:]
    # No clause boundary to cut on - the sentence is one clause with a trailing
    # qualifier ("Name the responsible role, evidence owner, and sign-off point
    # without adding new technology"). The head is already a claim, so trim to
    # it rather than dropping the statement, which is how unit 12 lost the only
    # line naming an accountable owner.
    if _has_predicate(cleaned):
        return label(cleaned, limit)
    return ""


# Truncating at a word count lands on whatever word is Nth: "Identify the first
# source assumption that no" is the same defect as cutting a claim in half, and
# it reached a rendered slide. A label may end on a content word or not at all.
_DANGLING = {
    "that", "which", "who", "whom", "whose", "no", "not", "the", "a", "an",
    "of", "in", "on", "at", "to", "by", "for", "from", "with", "as", "and",
    "or", "but", "if", "when", "is", "are", "was", "were", "be", "been",
    "its", "their", "this", "these", "those", "than", "then", "so",
}


def label(text: str, limit: int = 5) -> str:
    """A diagram node label: a short noun phrase, no predicate required.

    Node labels name a thing or a step, so the predicate test does not apply -
    but the label still has to end on a word boundary and never mid-token.
    """
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    cleaned = _FILLER.sub("", cleaned).strip(_TRAILING)
    # Drop a leading article: "the architectural design" -> "architectural design"
    cleaned = re.sub(r"^(?:the|a|an)\s+", "", cleaned, flags=re.I)
    words = _words(cleaned)
    if not words:
        return ""
    if len(words) <= limit:
        kept = words
    else:
        kept = words[:limit]
        # A conjunction inside the kept span means the sentence went on to a
        # second clause the label cannot carry. Ending before it reads as a
        # finished thought; ending after it promises one that never arrives.
        for i in range(len(kept) - 1, 2, -1):
            if kept[i].strip(_TRAILING).lower() in {"and", "or", "but", "then"}:
                kept = kept[:i]
                break
        while kept and kept[-1].strip(_TRAILING).lower() in _DANGLING:
            kept = kept[:-1]
    if len(kept) < 2:
        return ""
    out = " ".join(kept).strip(_TRAILING)
    return out[:1].upper() + out[1:]
