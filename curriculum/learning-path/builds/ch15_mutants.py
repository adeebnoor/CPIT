# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("unknown counts as met (the brochure reading)", '''
def fit(option, requirement):
    return FACTS.get((option, requirement), "met")
def shortlist(options):
    return [o for o in options if all(fit(o, r) == "met" for r in REQUIREMENTS)]
def evidence_needed(option):
    return [r for r in REQUIREMENTS if fit(option, r) == "unknown"]
'''),
    ("the shortlist removes known gaps only, so an option nobody has checked gets through", '''
def fit(option, requirement):
    return FACTS.get((option, requirement), "unknown")
def shortlist(options):
    return [o for o in options if all(fit(o, r) != "gap" for r in REQUIREMENTS)]
def evidence_needed(option):
    return [r for r in REQUIREMENTS if fit(option, r) == "unknown"]
'''),
    ("evidence_needed also lists known gaps", '''
def fit(option, requirement):
    return FACTS.get((option, requirement), "unknown")
def shortlist(options):
    return [o for o in options if all(fit(o, r) == "met" for r in REQUIREMENTS)]
def evidence_needed(option):
    return [r for r in REQUIREMENTS if fit(option, r) != "met"]
'''),
]
