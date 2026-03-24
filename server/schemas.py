from pydantic import BaseModel, Field

class VerseRequest(BaseModel):
    situation: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="The user's current situation or feeling. (e.g., 'My boss is bullying me', 'I feel lost')."
    )

class VerseResponse(BaseModel):
    verse: str = Field(
        ..., 
        description="The personalized and naturalized Bible verse."
    )
    ref: str = Field(
        ..., 
        description="The Bible reference (e.g., 'Psalms 37:7-8')."
    )