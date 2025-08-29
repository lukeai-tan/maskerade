import easyocr

reader = easyocr.Reader(["en"])


def merge_boxes(
    results, x_threshold: int = 20, y_threshold: int = 10, min_confidence: float = 0.5
):
    """
    Merge OCR boxes that are close horizontally and vertically.
    Returns list of tuples: (merged_bbox, merged_text, avg_confidence)
    """
    merged = []
    used = set()

    for i, (bbox1, text1, prob1) in enumerate(results):
        if prob1 < min_confidence:  # skip low-confidence text
            continue
        if i in used:
            continue
        x1s = [p[0] for p in bbox1]
        y1s = [p[1] for p in bbox1]
        x_min = min(x1s)
        x_max = max(x1s)
        y_min = min(y1s)
        y_max = max(y1s)
        merged_text = text1
        probs = [prob1]

        for j, (bbox2, text2, prob2) in enumerate(results):
            if prob2 < min_confidence or j <= i or j in used:
                continue
            x2s = [p[0] for p in bbox2]
            y2s = [p[1] for p in bbox2]
            x2_min, x2_max = min(x2s), max(x2s)
            y2_min, y2_max = min(y2s), max(y2s)

            if abs(x_min - x2_min) < x_threshold and abs(y_min - y2_min) < y_threshold:
                x_min = min(x_min, x2_min)
                x_max = max(x_max, x2_max)
                y_min = min(y_min, y2_min)
                y_max = max(y_max, y2_max)
                merged_text += " " + text2
                probs.append(prob2)
                used.add(j)

        merged_bbox = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        avg_prob = sum(probs) / len(probs)
        merged.append((merged_bbox, merged_text, avg_prob))

    return merged


def detect_text(img, min_confidence: float = 0.5):
    results = reader.readtext(img)
    merged_results = merge_boxes(results, min_confidence=min_confidence)
    return merged_results
