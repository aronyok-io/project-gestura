import math

GESTURES = {"Pointing_Up": "POINT", "Victory": "TWO_FINGERS", "Closed_Fist": "FIST",
            "Open_Palm": "OPEN_PALM", "Thumb_Up": "THUMB_UP", "Thumb_Down": "THUMB_DOWN"}


def pinch_ratio(hand, width, height):
    def distance(a, b):
        return math.hypot((a.x - b.x) * width, (a.y - b.y) * height)
    palm = distance(hand[0], hand[9])
    return distance(hand[4], hand[8]) / palm if palm > 0 else None


def sample_from_result(result, width, height):
    if not result.hand_landmarks:
        return {"gesture": "NONE", "position": None, "detected": False, "pinch_ratio": None}
    hand = result.hand_landmarks[0]
    gesture = "NONE"
    confidence = 0.0
    if result.gestures and result.gestures[0]:
        category = result.gestures[0][0]
        confidence = category.score
        if confidence >= 0.65:
            gesture = GESTURES.get(category.category_name, "NONE")
    return {"gesture": gesture, "position": (hand[8].x, hand[8].y), "detected": True,
            "pinch_ratio": pinch_ratio(hand, width, height), "confidence": confidence}
