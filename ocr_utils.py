import easyocr

reader: easyocr.Reader = easyocr.Reader(["en"])

# Each bbox is a list of 4 (x, y) tuples, text is str, prob is float
OCRBox = tuple[list[tuple[int, int]], str, float]
MergedBox = tuple[list[tuple[int, int]], str, float]


def merge_boxes(
    results: list[OCRBox],
    x_threshold: int = 20,
    y_threshold: int = 10,
    min_confidence: float = 0.5,
) -> list[MergedBox]:
    """
    Merge OCR boxes that are close horizontally and vertically.
    Returns list of tuples: (merged_bbox, merged_text, avg_confidence)
    """
    merged: list[MergedBox] = []
    used: set[int] = set()

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
        merged_text: str = text1
        probs: list[float] = [prob1]

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

        merged_bbox: list[tuple[int, int]] = [
            (x_min, y_min),
            (x_max, y_min),
            (x_max, y_max),
            (x_min, y_max),
        ]
        avg_prob: float = sum(probs) / len(probs)
        merged.append((merged_bbox, merged_text, avg_prob))

    return merged


def detect_text(
    img: object, min_confidence: float = 0.5
) -> list[MergedBox]:
    results: list[OCRBox] = reader.readtext(img) # type: ignore
    merged_results: list[MergedBox] = merge_boxes(results, min_confidence=min_confidence)
    return merged_results