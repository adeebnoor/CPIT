# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("minutes are forwarded without conversion", '''
def reserve_minutes(component, room_id, minutes):
    if type(minutes) is not int or not 1 <= minutes <= 120:
        raise ValueError("minutes must be a whole number from 1 to 120")
    r = component.reserve(room_id, minutes)
    if r["end"] - r["start"] != minutes:
        raise ContractError("wrong duration")
    return r
'''),
    ("out-of-range minutes reach the component", '''
def reserve_minutes(component, room_id, minutes):
    if type(minutes) is not int:
        raise ValueError("minutes must be a whole number")
    r = component.reserve(room_id, minutes * 60)
    if r["end"] - r["start"] != minutes * 60:
        raise ContractError("wrong duration")
    return r
'''),
    ("a fraction or True is accepted as minutes", '''
def reserve_minutes(component, room_id, minutes):
    if not isinstance(minutes, (int, float)) or not 1 <= minutes <= 120:
        raise ValueError("minutes must be from 1 to 120")
    r = component.reserve(room_id, int(minutes * 60))
    if r["end"] - r["start"] != int(minutes * 60):
        raise ContractError("wrong duration")
    return r
'''),
    ("the postcondition is never checked", '''
def reserve_minutes(component, room_id, minutes):
    if type(minutes) is not int or not 1 <= minutes <= 120:
        raise ValueError("minutes must be a whole number from 1 to 120")
    return component.reserve(room_id, minutes * 60)
'''),
]
