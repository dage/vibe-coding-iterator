from __future__ import annotations
from typing import Literal, Union, Annotated, Optional, List, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field

ISO = "%Y-%m-%dT%H:%M:%SZ"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(ISO)


class BaseEvent(BaseModel):
    t: str
    ts: str = Field(default_factory=now_iso)
    run_id: Optional[str] = None


class RunStarted(BaseEvent):
    t: Literal["run.started"]


class IterationStarted(BaseEvent):
    t: Literal["iteration.started"]
    n: int


class ContentText(BaseModel):
    type: Literal["text"]
    text: str


class ContentImage(BaseModel):
    type: Literal["image_url"]
    image_url: Dict[str, str]  # {"url": "..."} (data URL or /static path)


ContentPart = Union[ContentText, ContentImage]


class PromptSent(BaseEvent):
    t: Literal["prompt.sent"]
    actor: Literal["vision", "code", "user"]
    to: Literal["vision", "code"]
    content: List[ContentPart]
    iteration: int


class ResponseReceived(BaseEvent):
    t: Literal["response.received"]
    actor: Literal["vision", "code"]
    text: str
    iteration: int


class ScreenshotCaptured(BaseEvent):
    t: Literal["screenshot.captured"]
    url: str
    iteration: int


class ControlPaused(BaseEvent):
    t: Literal["control.paused"]


class ControlResumed(BaseEvent):
    t: Literal["control.resumed"]


class ErrorEv(BaseEvent):
    t: Literal["error"]
    msg: str
    where: Optional[str] = None


Event = Annotated[
    Union[
        RunStarted,
        IterationStarted,
        PromptSent,
        ResponseReceived,
        ScreenshotCaptured,
        ControlPaused,
        ControlResumed,
        ErrorEv,
    ],
    Field(discriminator="t"),
]


