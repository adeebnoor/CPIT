# Assignment 3 build: a fault tree for "the barrier closes while the zone is occupied".
# Tools: Event(name, source)  AND(a, b, ...)  OR(a, b, ...)  cut_sets(tree)  single_points(tree)
# source is "fact" (stated in the case), "assumption" or "proposed" (your new control or test).

current = OR(
    Event("CHANGE ME: a cause stated in the case", "fact"),
    Event("CHANGE ME: another cause", "assumption"),
)

revised = AND(
    Event("CHANGE ME: a cause", "fact"),
    Event("CHANGE ME: your proposed control", "proposed"),
)

# Your tests: at least three functions whose names start with test_
def test_example():
    assert cut_sets(current), "every tree has at least one cut set"
