#!/usr/bin/env python3
"""Check a caption against the page's contract before it can be queued.

The brain writes the caption and scores it (META PROMPT.md); this file checks
what a written instruction cannot enforce — the counts, the banned words, the
naming rule and the 80 floor — so a thin caption fails here instead of going
out on the page.

Three parts, exactly, no labels (MASTER PROMPT.md):

    The Fastest 1954 Mercedes 300SL Gullwing Ever Built        <- 5-11 words; either shape:
                                                                  certification (year + make +
                                                                  model + power word) or tease
                                                                  (the car named plus a claim)

    You have probably never climbed into a car through the roof. ... stare?
                                                                <- 3-5 sentences, 45-80 words, second
                                                                   person, ends on the question

     #Mercedes #ClassicCars #300SL #Gullwing #VintageMotorHouse  <- 4-5 tags, brand + classic + model

The score is checked as arithmetic, not as a claim: pass the five weights with
``--score-parts "23/19/18/14/16"`` and they must add up to ``--score``, with no weight over
its cap (hook shock 25, relatability 20, curiosity gap 20, shareability 15, visual wow 20).

Usage:

    python3 tools/caption.py check --title "..." --description "..." \\
        --hashtags "#Mercedes #ClassicCars #300SL" --score 88 \\
        --car "1954 Mercedes-Benz 300SL Gullwing"

Exit status is 1 when the caption fails, so a script can gate on it.
"""
from __future__ import annotations

import argparse
import re
import sys

# The power words MASTER PROMPT.md allows in the title.
POWER_WORDS = (
    "most imposing", "most overlooked", "most expensive", "most dangerous",
    "most secret", "most powerful", "most luxurious", "most forgotten",
    "rarest", "fastest", "biggest",
)

# The master's two title shapes. A title is legal under either one:
#
#   certification  year + make + model + one power word
#                  "The Rarest 1969 Ford Mustang Boss 429 Ever Made"
#   tease          the car, named, plus a claim about it
#                  "The Buick That Humiliated V8 Muscle Cars"
#
# Both are bound by the grounding test (could this title sit on a different car?), and
# no machine can run that test. The claim signal below is the proxy: the tease has to
# carry a verdict, a comparison or a figure, not just a model name and a mood. The
# reader still runs the grounding test before the film goes out.
CLAIM_RE = re.compile(
    r"\b(that|which|who|only|never|not|twice|three times|half|outran|outgunned|"
    r"beat|humbled|humiliated|killed|failed|flopped|sold|cost|built|made|stopped|"
    r"ended|saved|ruined|broke|refused|hid|tricked|shocked|insulted)\b", re.IGNORECASE)

# The caption's five weights, in the order the plan records them. They sum to 100, so a
# caption score that does not add up is a number someone typed, not a judgement.
SCORE_WEIGHTS = (("hook shock", 25), ("relatability", 20), ("curiosity gap", 20),
                 ("shareability", 15), ("visual wow", 20))

# Titles the page refuses (generic, no car, no claim).
BANNED_TITLE = (
    "check this out", "amazing car", "classic car video", "you won't believe",
    "must see", "wait for it", "look at this",
)

BANNED_TAGS = {"#viral", "#fyp", "#reels", "#trending", "#foryou", "#foryoupage"}

CLASSIC_TAGS = {"#classiccars", "#classiccar", "#classic", "#classiccarsdaily"}

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U0000200D\U000020E3]+"
)

YOU_RE = re.compile(r"\b(you|your|you're|you'd|you'll)\b", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
CTA_RE = re.compile(r"\b(comment|comments|tell us|tell me|which would|would you|"
                    r"drop your|type your|your pick)\b", re.IGNORECASE)

TITLE_MIN, TITLE_MAX = 5, 11
DESC_MIN_SENTENCES, DESC_MAX_SENTENCES = 3, 5
DESC_MIN_WORDS, DESC_MAX_WORDS = 45, 80
TAG_MIN, TAG_MAX = 4, 5
SCORE_GATE = 80


class Report:
    """The checks, in the order a reader wants them, with a pass/fail verdict."""

    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []
        self.failures: list[str] = []

    def ok(self, message: str) -> None:
        self.items.append(("ok", message))

    def bad(self, message: str) -> None:
        self.items.append(("FAIL", message))
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.items.append(("warn", message))

    @property
    def passed(self) -> bool:
        return not self.failures

    def render(self) -> str:
        width = max((len(label) for label, _ in self.items), default=0)
        lines = ["caption check"]
        for label, message in self.items:
            lines.append("  %-*s  %s" % (width, label, message))
        if self.passed:
            lines.append("  -> passes" + (" (with warnings)" if any(
                label == "warn" for label, _ in self.items) else ""))
        else:
            lines.append("  -> FAILS (%d)" % len(self.failures))
        return "\n".join(lines)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    return (text or "").split()


def words_in(text: str) -> int:
    return len(words(text))


def _car_parts(car: str) -> tuple[str, list[str]]:
    """(year, model tokens) from ``--car`` — '1954 Mercedes-Benz 300SL Gullwing'."""
    car = " ".join((car or "").split())
    match = YEAR_RE.search(car)
    year = match.group(0) if match else ""
    rest = YEAR_RE.sub(" ", car).split()
    if len(rest) > 1 and not rest[0].islower():
        rest = rest[1:]  # drop the make, keep the model words
    return year, [t for t in rest if len(t) > 1]


def _make_tokens(car: str) -> list[str]:
    """Spellings a brand tag may use: 'Mercedes-Benz' -> mercedesbenz, mercedes."""
    car = " ".join((car or "").split())
    rest = [t for t in YEAR_RE.sub(" ", car).split() if len(t) > 1]
    if not rest:
        return []
    make = re.sub(r"[^a-z0-9]", "", rest[0].lower())
    first = re.sub(r"[^a-z0-9]", "", rest[0].lower().split("-")[0])
    return [t for t in dict.fromkeys((make, first)) if t]


def _plural(count: int, noun: str) -> str:
    return "%d %s%s" % (count, noun, "" if count == 1 else "s")


def check_title(title: str, car: str, report: Report) -> None:
    count = words_in(title)
    if TITLE_MIN <= count <= TITLE_MAX:
        report.ok("title        %s" % _plural(count, "word"))
    else:
        report.bad("title        %s — the band is %d–%d"
                   % (_plural(count, "word"), TITLE_MIN, TITLE_MAX))

    if title.rstrip().endswith((".", "!", "?")):
        report.bad("title        ends with punctuation — a headline takes none")

    lowered = title.lower()
    banned = [phrase for phrase in BANNED_TITLE if phrase in lowered]
    if banned:
        report.bad("title        generic: \"%s\"" % banned[0])

    power = [word for word in POWER_WORDS if re.search(r"\b%s\b" % re.escape(word), lowered)]
    year = YEAR_RE.search(title)
    model: list[str] = []
    makes: list[str] = []
    if car:
        wanted_year, model_tokens = _car_parts(car)
        makes = _make_tokens(car)
        if wanted_year and year and wanted_year != year.group(0):
            report.bad("title        names %s, the car is %s" % (year.group(0), wanted_year))
        model = [t for t in model_tokens if t.lower() in lowered]

    # -- shape 1: certification, year + make + model + one power word ------------------
    certification_ok = bool(year) and bool(power)
    if car and not model:
        certification_ok = False

    # -- shape 2: tease, the car named plus a claim -----------------------------------
    # Digits count as a claim, but the year is the car's name rather than a claim, so it
    # is removed before looking for a figure.
    claim_text = YEAR_RE.sub(" ", title.lower())
    claim = re.search(r"\d", claim_text) or CLAIM_RE.search(claim_text)
    named = bool(model) or any(m in lowered for m in makes)
    tease_ok = named and bool(claim)

    if certification_ok:
        report.ok("title        certification shape: year + model + %s" % power[0].title())
    elif tease_ok:
        report.ok("title        tease shape: %s" % (
            model[0] if model else makes[0].title()))
        report.warn("title        tease shape — run the grounding test: could this title "
                    "sit on a different car's post?")
    else:
        if not year and not tease_ok:
            report.bad("title        no year, and not a tease either — a mood line, "
                       "not a headline")
        if not power and not tease_ok:
            report.bad("title        no power word (%s) — or make it a tease that "
                       "claims something" % ", ".join(w.title() for w in POWER_WORDS[:3]))
        if car and not named:
            report.bad("title        does not name the car (%s)" % car)
        if not claim and named:
            report.bad("title        names the car but claims nothing — the tease needs "
                       "a verdict, a comparison or a figure")

    if year:
        report.ok("title        names the year %s" % year.group(0))
    if model:
        report.ok("title        names the model: %s" % model[0])
    elif car and named:
        report.ok("title        names the make")
    if not car:
        report.warn("title        no --car given: model and year not compared")


def check_description(description: str, title: str, report: Report) -> None:
    body = (description or "").strip()
    if not body:
        report.bad("description  empty — the post needs a real paragraph")
        return

    count = len(sentences(body))
    if DESC_MIN_SENTENCES <= count <= DESC_MAX_SENTENCES:
        report.ok("description  %s" % _plural(count, "sentence"))
    else:
        report.bad("description  %s — the band is %d–%d"
                   % (_plural(count, "sentence"),
                      DESC_MIN_SENTENCES, DESC_MAX_SENTENCES))

    word_count = words_in(body)
    if DESC_MIN_WORDS <= word_count <= DESC_MAX_WORDS:
        report.ok("description  %s" % _plural(word_count, "word"))
    else:
        report.bad("description  %s — the band is %d–%d (a one-liner is not accepted)"
                   % (_plural(word_count, "word"), DESC_MIN_WORDS, DESC_MAX_WORDS))

    if YOU_RE.search(body):
        report.ok("description  speaks to \"you\"")
    else:
        report.bad("description  never says \"you\" — it is a caption, not a fact sheet")

    last = sentences(body)[-1] if sentences(body) else ""
    if last.rstrip().endswith("?"):
        report.ok("description  ends on a question")
    elif CTA_RE.search(last):
        report.warn("description  ends on a call to action, not a question mark")
    else:
        report.bad("description  no question to answer in the comments")

    if body.rstrip().endswith(".") is False and body.rstrip().endswith("?") is False:
        report.bad("description  does not end on a full stop or a question mark")

    if "#" in body:
        report.bad("description  carries a hashtag — hashtags are the third part only")
    if "http" in body.lower() or "link in bio" in body.lower():
        report.bad("description  carries a link — the page posts no links")
    emoji = EMOJI_RE.search(body)
    if emoji:
        report.bad("description  carries an emoji (%s)" % emoji.group(0))

    if title and body.lower().startswith(title.lower()):
        report.bad("description  reopens with the title — sentence one is the hook, not a repeat")


def check_hashtags(hashtags: str, car: str, report: Report) -> None:
    raw = hashtags or ""
    tags = raw.split()
    if not tags:
        report.bad("hashtags     none")
        return

    # The leading space the page's block starts with is normalised away by
    # `queue` before the caption is stored, so it is not checked here.
    bad = [t for t in tags if not t.startswith("#")]
    if bad:
        report.bad("hashtags     not a tag: %s" % bad[0])

    if TAG_MIN <= len(tags) <= TAG_MAX:
        report.ok("hashtags     %d tags" % len(tags))
    else:
        report.bad("hashtags     %d tags — the band is %d–%d"
                   % (len(tags), TAG_MIN, TAG_MAX))

    lowered = [t.lower() for t in tags]
    spam = [t for t in lowered if t in BANNED_TAGS]
    if spam:
        report.bad("hashtags     spam tag %s" % spam[0])

    if any(t in CLASSIC_TAGS for t in lowered):
        report.ok("hashtags     a classic-car tag")
    else:
        report.bad("hashtags     no classic-car tag (#ClassicCars)")

    if car:
        makes = _make_tokens(car)
        if makes and any(make in tag for make in makes for tag in lowered):
            report.ok("hashtags     the brand's tag")
        elif makes:
            report.bad("hashtags     no brand tag (#%s)" % makes[0].title())
        _, model_tokens = _car_parts(car)
        # A tag drops punctuation ("SC/Rambler" -> #SCRambler), so compare bare letters.
        flat_tags = [re.sub(r"[^a-z0-9]", "", t) for t in lowered]
        if model_tokens and not any(
                re.sub(r"[^a-z0-9]", "", tok.lower()) in tag
                for tok in model_tokens for tag in flat_tags):
            report.warn("hashtags     no model tag (%s)" % model_tokens[0])


def parse_parts(parts):
    """The five sub-scores from '23/19/18/14/16' or 'hook 23, relatability 19, …'.

    Returns ``None`` when there is nothing to read, so an un-itemised score can be warned
    about rather than silently accepted.
    """
    if parts is None:
        return None
    if isinstance(parts, str):
        found = re.findall(r"\d{1,3}", parts)
    else:
        found = [str(p) for p in parts]
    if not found:
        return None
    return [int(n) for n in found]


def check_score(score, report: Report, parts=None) -> None:
    if score is None:
        report.bad("score        none recorded — the brain scores the caption, "
                   "pass --caption-score")
        return
    try:
        value = int(score)
    except (TypeError, ValueError):
        report.bad("score        %r is not a number" % (score,))
        return
    if not 0 <= value <= 100:
        report.bad("score        %d is outside 0–100" % value)
        return
    if value < SCORE_GATE:
        report.bad("score        %d/100 — below the gate of %d, rewrite it"
                   % (value, SCORE_GATE))
        return

    # A score is a judgement, so it has to be five judgements that add up.
    marks = parse_parts(parts)
    if not marks:
        report.warn("score        %d/100, not itemised — pass --score-parts "
                    "\"23/19/18/14/16\" so the total can be added up" % value)
        return
    if len(marks) != len(SCORE_WEIGHTS):
        report.bad("score        %d sub-score(s) — the five weights are %s"
                   % (len(marks), "/".join(str(w) for _, w in SCORE_WEIGHTS)))
        return
    over = ["%s %d/%d" % (name, got, cap)
            for (name, cap), got in zip(SCORE_WEIGHTS, marks) if got > cap]
    if over:
        report.bad("score        a weight is scored above its cap: %s" % ", ".join(over))
        return
    total = sum(marks)
    itemised = ", ".join("%s %d/%d" % (name, got, cap)
                         for (name, cap), got in zip(SCORE_WEIGHTS, marks))
    if total != value:
        report.bad("score        the parts add to %d, the score says %d (%s)"
                   % (total, value, itemised))
        return
    report.ok("score        %d/100 = %s (gate %d)" % (value, itemised, SCORE_GATE))


def report_for(title: str, description: str, hashtags: str, score,
               car: str = "", parts=None) -> Report:
    report = Report()
    check_title(" ".join((title or "").split()), car, report)
    check_description(" ".join((description or "").split()), title, report)
    check_hashtags(hashtags or "", car, report)
    check_score(score, report, parts)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="check one caption")
    p_check.add_argument("--title", required=True)
    p_check.add_argument("--description", required=True)
    p_check.add_argument("--hashtags", default="")
    p_check.add_argument("--score", type=int, default=None,
                         help="the caption score the brain gave it (gate 80)")
    p_check.add_argument("--car", default="",
                         help='e.g. "1954 Mercedes-Benz 300SL Gullwing"')
    p_check.add_argument("--score-parts", default=None,
                         help='the five weights, e.g. "23/19/18/14/16" '
                              '(hook/relatability/curiosity/shareability/wow)')

    args = parser.parse_args()
    report = report_for(args.title, args.description, args.hashtags,
                        args.score, args.car, args.score_parts)
    print(report.render())
    if not report.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
