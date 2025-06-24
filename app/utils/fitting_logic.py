def get_target_ranges(position: str):
    """Returns ideal joint angle ranges (min, max) for a given position."""
    ranges = {
        "comfort": {
            "knee": (145, 155),
            "hip": (85, 100),
            "elbow": (150, 170),
        },
        "sport": {
            "knee": (140, 150),
            "hip": (75, 90),
            "elbow": (145, 165),
        },
        "aero": {
            "knee": (135, 145),
            "hip": (65, 80),
            "elbow": (140, 160),
        },
    }
    return ranges.get(position.lower(), ranges["sport"])


def generate_fit_suggestions(joint_angles: dict, position: str):
    target_ranges = get_target_ranges(position)
    suggestions = {}

    def suggest(
        joint: str,
        part: str,
        action_if_low: str,
        action_if_high: str,
        mm_per_degree: int,
    ):
        angle = joint_angles.get(joint)
        if angle is None:
            suggestions[joint] = "Could not measure angle."
            return

        low, high = target_ranges[joint]
        if angle < low:
            delta = round((low - angle) * mm_per_degree)
            suggestions[joint] = (
                f"{joint.capitalize()} angle too low ({angle} degrees). "
                f"Issue: {part.capitalize()}. {action_if_low.capitalize()} by ~{delta} mm."
            )
        elif angle > high:
            delta = round((angle - high) * mm_per_degree)
            suggestions[joint] = (
                f"{joint.capitalize()} angle too high ({angle} degrees). "
                f"Issue: {part.capitalize()}. {action_if_high.capitalize()} by ~{delta} mm."
            )
        else:
            suggestions[joint] = (
                f"{joint.capitalize()} angle in optimal range ({angle}°)."
            )

    suggest(
        "knee",
        "saddle height",
        "raise the saddle",
        "lower the saddle",
        6,
    )
    suggest(
        "hip",
        "saddle fore/aft",
        "move saddle forward",
        "move saddle back",
        5,
    )
    suggest(
        "elbow",
        "handlebar height",
        "lower the bars",
        "raise the bars",
        10,
    )

    return suggestions
