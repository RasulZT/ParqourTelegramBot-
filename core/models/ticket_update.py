from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class TicketUpdateData:
    id: int
    asana_issue_id: str
    summary: str
    description: Optional[str]
    criticality_level: Optional[str]
    problem_area: Optional[str]
    project: Optional[str]
    section: Optional[str]
    is_ticket_closed: bool
    asana_issue_status: Optional[str]
    comments_updated_time: Optional[str]
    changes: Dict[str, Dict[str, Any]]

    @staticmethod
    def from_dict(data: dict) -> "TicketUpdateData":
        ticket = data.get("full_ticket", {})
        changes = data.get("changes", {})

        return TicketUpdateData(
            id=data.get("id"),
            asana_issue_id=ticket.get("asana_issue_id"),
            summary=ticket.get("summary"),
            description=ticket.get("description"),
            criticality_level=ticket.get("criticality_level"),
            problem_area=ticket.get("problem_area"),
            project=ticket.get("project"),
            section=ticket.get("section"),
            is_ticket_closed=ticket.get("is_ticket_closed", False),
            asana_issue_status=ticket.get("asana_issue_status"),
            comments_updated_time=ticket.get("comments_updated_time"),
            changes=changes
        )
