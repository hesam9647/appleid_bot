from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from app.database import Ticket, TicketMessage, User

class TicketService:
    def __init__(self, session: Session):
        self.session = session

    async def create_ticket(self, user_id: int, title: str, first_message: str) -> Ticket:
        # Create ticket
        ticket = Ticket(
            user_id=user_id,
            title=title
        )
        self.session.add(ticket)
        await self.session.flush()
        
        # Add first message
        message = TicketMessage(
            ticket_id=ticket.id,
            sender_id=user_id,
            content=first_message
        )
        self.session.add(message)
        await self.session.commit()
        
        return ticket

    async def add_message(
        self, 
        ticket_id: int, 
        sender_id: int, 
        content: str, 
        file_id: str = None,
        message_type: str = 'text',
        is_from_admin: bool = False
    ) -> TicketMessage:
        message = TicketMessage(
            ticket_id=ticket_id,
            sender_id=sender_id,
            content=content,
            file_id=file_id,
            message_type=message_type,
            is_from_admin=is_from_admin
        )
        self.session.add(message)
        
        # Update ticket status and time
        ticket = await self.get_ticket(ticket_id)
        if ticket:
            ticket.status = 'answered' if is_from_admin else 'in_progress'
            ticket.updated_at = datetime.utcnow()
        
        await self.session.commit()
        return message

    async def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_user_tickets(self, user_id: int) -> List[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.updated_at.desc())
        )
        return result.scalars().all()

    async def get_ticket_messages(self, ticket_id: int) -> List[TicketMessage]:
        result = await self.session.execute(
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket_id)
            .order_by(TicketMessage.created_at)
        )
        return result.scalars().all()

    async def get_open_tickets(self) -> List[Ticket]:
        result = await self.session.execute(
            select(Ticket)
            .where(Ticket.status.in_(['open', 'in_progress']))
            .order_by(Ticket.priority.desc(), Ticket.created_at)
        )
        return result.scalars().all()

    async def close_ticket(self, ticket_id: int) -> bool:
        try:
            await self.session.execute(
                update(Ticket)
                .where(Ticket.id == ticket_id)
                .values(status='closed')
            )
            await self.session.commit()
            return True
        except:
            return False

    async def set_priority(self, ticket_id: int, priority: str) -> bool:
        try:
            await self.session.execute(
                update(Ticket)
                .where(Ticket.id == ticket_id)
                .values(priority=priority)
            )
            await self.session.commit()
            return True
        except:
            return False
