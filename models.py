from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatMessage:
    sender: str
    receiver: str
    content: str = ""
    file_name: str = ""
    file_path: str = ""
    msg_type: str = "text"
    timestamp: str = ""
