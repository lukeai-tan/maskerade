from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

analyzer = AnalyzerEngine()

# Custom recognizer for full credit card numbers
credit_card_pattern = Pattern(
    name="credit_card_full",
    regex=r"\b(?:\d[ -]*?){13,16}\b",
    score=0.8
)
cc_recognizer = PatternRecognizer(supported_entity="CREDIT_CARD_NUMBER", patterns=[credit_card_pattern])
analyzer.registry.add_recognizer(cc_recognizer)

def analyze_pii(text):
    return analyzer.analyze(
        text=text,
        entities=[
            #"PERSON",
            "PHONE_NUMBER",
            "EMAIL_ADDRESS",
            "US_SSN",
            "CREDIT_CARD_NUMBER",
            "NRP",
            "LOCATION",
            "IP_ADDRESS",
            "IBAN_CODE",
            "US_DRIVER_LICENSE",
            "US_PASSPORT"
        ],
        language="en"
    )

