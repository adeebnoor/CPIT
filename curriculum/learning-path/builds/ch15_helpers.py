# The supplied facts, exactly as in the scenario. Anything not listed is not known.
FACTS = {
    ("A", "booking"): "met", ("A", "recurring"): "met", ("A", "support-3-years"): "gap",
    ("B", "booking"): "met", ("B", "recurring"): "gap", ("B", "support-3-years"): "met",
}
REQUIREMENTS = ["booking", "recurring", "export-api", "support-3-years", "peak-load"]
