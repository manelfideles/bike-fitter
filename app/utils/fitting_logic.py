# TODO - CHATGPT generated these. Should these ranges be dynamically determined based on physical rider features?
TARGETS = {
    "top": {
        "knee": (60, 70),
        "hip": (45, 55),
    },
    "bottom": {
        "knee": (140, 150),
        "hip": (70, 85),
    },
    "any": {
        "back": (35, 45),  # angle with horizontal
        "shoulder": (75, 90),  # arm-to-torso angle
        "arm": (140, 160),  # elbow angle
    },
}


def quantify_adjustment(joint: str, pos: str, angle: float):
    low, high = TARGETS[pos][joint]
    delta = 0
    if angle < low:
        delta = angle - low
    elif angle > high:
        delta = angle - high
    return delta


def describe_adjustment(joint: str, pos: str, delta: float):
    if joint == "knee" and pos == "bottom":
        mm = round(delta * 2.5)
        return f"{'Lower' if mm > 0 else 'Increase'} saddle height by {abs(mm)} mm."
    if joint == "hip" and pos == "top":
        mm = round(delta * 3)
        return f"Move saddle {abs(mm)} mm {'backward' if mm > 0 else 'forward'}."
    if joint == "back":
        mm = round(delta * 5)
        return f"{'Increase' if mm > 0 else 'Shorten'} handlebar reach by {abs(mm)} mm."
    if joint == "shoulder":
        mm = round(delta * 5)
        return f"{'Lower' if mm > 0 else 'Raise'} handlebar drop by {abs(mm)} mm."
    return "No adjustment needed."


def suggest_range(joint: str, pos: str, angle: float):
    low, high = TARGETS[pos][joint]
    default = f"{joint.capitalize()} angle: {angle:.1f} degrees. Recommended range: ({low}, {high})."

    delta = quantify_adjustment(joint, pos, angle)
    adjustment = describe_adjustment(joint, pos, delta)
    return " ".join([default, adjustment])


def generate_fit_suggestions(angle_data: dict[str, dict[str, float]]):
    suggestions = {}
    for pos in ["top", "bottom"]:
        for joint in TARGETS[pos]:
            angle = angle_data.get(pos, {}).get(joint)
            if angle:
                suggestions[f"{joint}_{pos}"] = suggest_range(joint, pos, angle)
    for joint in TARGETS["any"]:
        vals = [
            angle_data.get(p, {}).get(joint)
            for p in ["top", "bottom"]
            if joint in angle_data.get(p, {})
        ]
        if vals:
            avg = sum(vals) / len(vals)
            suggestions[joint] = suggest_range(joint, "any", avg)
    return suggestions
