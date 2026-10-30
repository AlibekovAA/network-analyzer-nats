from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel


class NetworkPacket(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str
    size: int
    timestamp: str
    additional_info: dict | None = None


class NetworkAnalysisResult(BaseModel):
    packets: list[NetworkPacket]
    summary: dict


@dataclass
class ChunkInfo:
    number: int
    data: bytes
    total_chunks: int


class AnalysisMessage(BaseModel):
    analysis_id: str
    chunk_number: int | None = None
    total_chunks: int
    data: str | None = None
    encoding: Literal["hex", "base64"]
