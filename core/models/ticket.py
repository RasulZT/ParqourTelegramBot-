from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


@dataclass
class UserInfo:
    id: int
    telegram_id: int
    telegram_fullname: str
    role: str
    phone: Optional[str]
    kaspi_phone: Optional[str]
    address: Optional[str]
    bonus: Optional[int]


@dataclass
class ParkingInfo:
    id: int
    name: str
    host: str
    ip: str
    group_name: str
    group_chat_id: Optional[int]


class AsanaIssueStatus(str, Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TicketSection(str, Enum):
    NEW = "NEW"
    INBOX = "INBOX"
    COMPLETED = "COMPLETED"


@dataclass
class Ticket:
    id: int
    asana_issue_id: Optional[str]
    project: Optional[str]
    problem_area: Optional[str]
    criticality_level: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    message_id: Optional[int]
    comments_updated_time: Optional[str]
    is_ticket_closed: bool
    asana_issue_status: str
    section: str
    user: Optional[UserInfo] = None
    parking: Optional[ParkingInfo] = None


@dataclass
class TicketSerializer:
    @staticmethod
    def to_dict(ticket: Ticket) -> Dict[str, Any]:
        return {
            "id": ticket.id,
            "asana_issue_id": ticket.asana_issue_id,
            "user_id": ticket.user.telegram_id if ticket.user else None,
            "parking_id": ticket.parking.id if ticket.parking else None,
            "project": ticket.project,
            "problem_area": ticket.problem_area,
            "criticality_level": ticket.criticality_level,
            "summary": ticket.summary,
            "description": ticket.description,
            "message_id": ticket.message_id,
            "comments_updated_time": ticket.comments_updated_time,
            "is_ticket_closed": ticket.is_ticket_closed,
            "asana_issue_status": ticket.asana_issue_status,
            "section": ticket.section
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Ticket:
        user_data = data.get("user")
        parking_data = data.get("parking")
        return Ticket(
            id=data["id"],
            asana_issue_id=data.get("asana_issue_id"),
            project=data.get("project"),
            problem_area=data.get("problem_area"),
            criticality_level=data.get("criticality_level"),
            summary=data.get("summary"),
            description=data.get("description"),
            message_id=data.get("message_id"),
            comments_updated_time=data.get("comments_updated_time"),
            is_ticket_closed=data.get("is_ticket_closed", False),
            asana_issue_status=data.get("asana_issue_status", "CREATED"),
            section=data.get("section", "NEW"),
            user=UserInfo(**user_data) if user_data else None,
            parking=ParkingInfo(**parking_data) if parking_data else None
        )
