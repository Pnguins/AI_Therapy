from pydantic import BaseModel, Field
from typing import Dict

class MentalHealthClassification(BaseModel):
    classification: Dict[str, float] = Field(description="Classification of mental health issues")