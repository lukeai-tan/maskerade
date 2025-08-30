from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer import RecognizerResult

analyzer = AnalyzerEngine()

# Custom recognizer for full credit card numbers
credit_card_pattern: Pattern = Pattern(
    name="credit_card_full", regex=r"\b(?:\d[ -]*?){13,16}\b", score=0.8
)
cc_recognizer: PatternRecognizer = PatternRecognizer(
    supported_entity="CREDIT_CARD_NUMBER", patterns=[credit_card_pattern]
)
analyzer.registry.add_recognizer(cc_recognizer)


def analyze_pii(text: str) -> list[RecognizerResult]:
    return analyzer.analyze(
        text=text,
        entities=[
            "PERSON",
            "CRYPTO",  # Bitcoin wallets
            "PHONE_NUMBER",  # local & international phone numbers
            "EMAIL_ADDRESS",
            "US_SSN",  # U.S. Social Security Numbers
            "CREDIT_CARD",
            "NRP",  # Nationality, Religious, Political groups
            "LOCATION",  # city, country, addresses
            "IP_ADDRESS",  # IPv4 + IPv6 addresses
            "IBAN_CODE",  # international bank account numbers
            "US_DRIVER_LICENSE",  # US Driver License
            "US_PASSPORT",  # US Passport Number
            "SG_NRIC_FIN",  # SG NRIC
        ],
        language="en",
    )
