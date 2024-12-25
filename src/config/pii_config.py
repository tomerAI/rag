PII_SETTINGS = {
    "ENTITY_TYPES": {
        "MASK_FOR_LLM": [
            "person", "email", "phone", "credit_card", "ssn"
        ],
        "PRESERVE_FOR_SEARCH": [
            "organization", "location", "date"
        ]
    },
    "THRESHOLD": 0.5,
    "MODEL_NAME": "urchade/gliner_medium-v2.1"
}
