from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Rule(BaseModel):
    id: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    action: str
    priority: int
    description: str


class Node(BaseModel):
    name: str
    ip: str
    listen_port: int
    last_seen: Optional[datetime] = None


class Event(BaseModel):
    id: Optional[str] = None
    node_name: str
    src_ip: str
    dst_ip: Optional[str] = None
    protocol: str
    port: int
    action: str
    timestamp: Optional[datetime] = None


class RegisterRequest(BaseModel):
    name: str
    ip: str
    listen_port: int


class PacketInfo(BaseModel):
    src_ip: str
    dst_ip: Optional[str] = None
    protocol: str
    src_port: Optional[int] = None
    dst_port: int
