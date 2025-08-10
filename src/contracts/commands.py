from __future__ import annotations
from typing import Literal, List, Union, Dict
from pydantic import BaseModel


class ControlCommand(BaseModel):
    action: Literal["pause", "resume"]


class ContentText(BaseModel):
    type: Literal["text"]
    text: str


class ContentImage(BaseModel):
    type: Literal["image_url"]
    image_url: Dict[str, str]  # {"url":"..."}


ContentPart = Union[ContentText, ContentImage]


class PromptCommand(BaseModel):
    actor: Literal["user"]  # from UI
    route_to: Literal["vision", "code"]
    content: List[ContentPart]


