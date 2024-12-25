from gliner import GLiNER
from typing import List, Dict, Tuple
import uuid

class PIIHandler:
    def __init__(self):
        self.model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        self.pii_mapping = {}
        self.labels = [
            "person", "organization", "location", "date", 
            "email", "phone", "credit_card", "ssn"
        ]
        
    def _generate_placeholder(self, label: str) -> str:
        return f"<{label}_{uuid.uuid4().hex[:8]}>"
        
    def identify_entities(self, text: str) -> List[Dict]:
        return self.model.predict_entities(text, self.labels, threshold=0.5)
        
    def mask_entities(self, text: str, entities: List[Dict]) -> Tuple[str, Dict]:
        masked_text = text
        for entity in sorted(entities, key=lambda x: len(x["text"]), reverse=True):
            if entity["text"] not in self.pii_mapping:
                self.pii_mapping[entity["text"]] = self._generate_placeholder(entity["label"])
            masked_text = masked_text.replace(entity["text"], self.pii_mapping[entity["text"]])
        return masked_text
        
    def restore_entities(self, text: str) -> str:
        restored_text = text
        for original, placeholder in self.pii_mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
