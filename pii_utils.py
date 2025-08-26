from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

analyzer = AnalyzerEngine()

# Custom recognizer for full credit card numbers
cc_pattern = Pattern(
    name="credit_card_full",
    regex=r"\b(?:\d[ -]*?){13,16}\b",
    score=0.9
)
cc_recognizer = PatternRecognizer(supported_entity="CREDIT_CARD", patterns=[cc_pattern])
analyzer.registry.add_recognizer(cc_recognizer)

def analyze_pii(text):
    return analyzer.analyze(text=text, language="en")
