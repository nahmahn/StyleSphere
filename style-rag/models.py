from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ─────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────

class ConversationState(BaseModel):
    category_filter: Optional[str] = Field(default=None, description="Selected category")
    color_filter: Optional[str] = Field(default=None, description="Selected color")
    style_filter: Optional[str] = Field(default=None, description="Selected style")
    occasion_filter: Optional[str] = Field(default=None, description="Selected occasion")
    brand_filter: Optional[str] = Field(default=None, description="Selected brand")
    last_mentioned_item: Optional[str] = Field(default=None, description="Last item mentioned in conversation")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's current chat message")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="List of past messages and responses")
    state: ConversationState = Field(default_factory=ConversationState, description="Current conversation filters/state")


class ItemMetadata(BaseModel):
    item_id: str
    category: str
    tags: List[str]
    full_description: str


class ChatResponse(BaseModel):
    response: str
    items: List[ItemMetadata]
    state: ConversationState


# ─────────────────────────────────────────────
# Utility: Query Type Detector
# ─────────────────────────────────────────────

def is_new_query(message: str) -> bool:
    """
    Detect if the user's message is a new clothing search or a refinement.
    """
    keywords = ["t-shirt", "shirt", "blouse", "top", "jeans", "jacket", "dress",
                "clothes", "v neck", "long sleeve", "buttoned", "purple", "tank top"]
    message = message.lower()
    return any(kw in message for kw in keywords)


# ─────────────────────────────────────────────
# Example Handler (Mock)
# ─────────────────────────────────────────────

def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """
    Handle a chat request and reset filters if it's a new query.
    """
    if is_new_query(request.message):
        request.state = ConversationState()  # Reset filters

    # Mock items
    dummy_items = [
        ItemMetadata(
            item_id="001",
            category="TOPS",
            tags=["Blouse", "Shirring", "Feminine"],
            full_description="A stylish shirred feminine blouse."
        ),
        ItemMetadata(
            item_id="002",
            category="TOPS",
            tags=["T-shirt", "Drop shoulder", "Casual"],
            full_description="Casual drop-shoulder t-shirt in soft cotton."
        )
    ]

    return ChatResponse(
        response=f"I found some great options for '{request.message}'!",
        items=dummy_items,
        state=request.state
    )
