# The supplied facts, exactly as in the scenario. Anything not listed is not known.
# A: "the required booking functions and an export API; its support commitment ends after two years".
# B: "lacks recurring bookings and has no measured peak-load results".
FACTS = {
    ("A", "booking"): "met", ("A", "recurring"): "met", ("A", "export-api"): "met", ("A", "support-3-years"): "gap",
    ("B", "booking"): "met", ("B", "recurring"): "gap",
}
REQUIREMENTS = ["booking", "recurring", "export-api", "support-3-years", "peak-load"]
