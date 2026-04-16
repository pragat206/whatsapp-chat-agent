"""Seed script — creates initial admin user and demo data."""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.audit import Setting
from app.models.contact import Contact
from app.models.conversation import Conversation, Message, MessageDirection, MessageStatus, Tag
from app.models.lead import Lead
from app.models.product import Product, ProductCategory
from app.models.user import Role, User


async def seed():
    async with async_session_factory() as session:
        # Check if already seeded
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        # Get roles
        roles_result = await session.execute(select(Role))
        roles = {r.name: r for r in roles_result.scalars().all()}

        # Create admin user
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("admin123456"),
            full_name="System Admin",
            is_active=True,
            is_verified=True,
        )
        admin.roles = [roles.get("super_admin", roles.get("admin"))]
        session.add(admin)

        # Create operator user
        operator = User(
            email="operator@example.com",
            hashed_password=hash_password("operator123456"),
            full_name="Support Operator",
            is_active=True,
            is_verified=True,
        )
        operator.roles = [roles.get("operator")]
        session.add(operator)

        # Create analyst user
        analyst = User(
            email="analyst@example.com",
            hashed_password=hash_password("analyst123456"),
            full_name="Business Analyst",
            is_active=True,
            is_verified=True,
        )
        analyst.roles = [roles.get("analyst")]
        session.add(analyst)

        # Create tags
        tags = []
        for name, color in [
            ("Hot Lead", "#ef4444"),
            ("Support", "#3b82f6"),
            ("Complaint", "#f97316"),
            ("Follow-up", "#8b5cf6"),
            ("Closed Won", "#22c55e"),
            ("Closed Lost", "#6b7280"),
        ]:
            tag = Tag(name=name, color=color)
            session.add(tag)
            tags.append(tag)

        # Create product categories
        cat_electronics = ProductCategory(name="Electronics", description="Electronic devices and accessories")
        cat_software = ProductCategory(name="Software", description="Software products and licenses")
        session.add(cat_electronics)
        session.add(cat_software)

        # Create sample products
        product1 = Product(
            name="SmartHome Hub Pro",
            sku="SH-HUB-001",
            description="AI-powered smart home controller with voice control and automation",
        )
        product1.categories = [cat_electronics]
        session.add(product1)

        product2 = Product(
            name="CloudSync Business Suite",
            sku="CS-BIZ-001",
            description="Enterprise cloud collaboration and project management platform",
        )
        product2.categories = [cat_software]
        session.add(product2)

        # Create sample contacts
        contact1 = Contact(
            phone_number="+919876543210",
            display_name="Rahul Kumar",
            city="Mumbai",
            language="en",
        )
        session.add(contact1)

        contact2 = Contact(
            phone_number="+919876543211",
            display_name="Priya Sharma",
            city="Delhi",
            language="hi",
        )
        session.add(contact2)

        await session.flush()

        # Create sample conversations
        conv1 = Conversation(
            contact_id=contact1.id,
            status="active",
            state="faq",
            language="en",
            message_count=4,
        )
        session.add(conv1)

        conv2 = Conversation(
            contact_id=contact2.id,
            status="resolved",
            state="idle",
            language="hi",
            message_count=2,
        )
        session.add(conv2)

        await session.flush()

        # Add sample messages
        messages = [
            Message(conversation_id=conv1.id, direction=MessageDirection.INBOUND, content="Hi, I want to know about SmartHome Hub", status=MessageStatus.DELIVERED),
            Message(conversation_id=conv1.id, direction=MessageDirection.OUTBOUND, content="Hello Rahul! The SmartHome Hub Pro is our AI-powered smart home controller. It features voice control and home automation. Would you like to know about pricing or features?", status=MessageStatus.DELIVERED, is_ai_generated=True),
            Message(conversation_id=conv1.id, direction=MessageDirection.INBOUND, content="What features does it have?", status=MessageStatus.DELIVERED),
            Message(conversation_id=conv1.id, direction=MessageDirection.OUTBOUND, content="The SmartHome Hub Pro includes:\n• Voice control (Alexa & Google compatible)\n• Automated routines & scheduling\n• Energy monitoring\n• Security integration\n• Mobile app control\n\nWould you like more details on any specific feature?", status=MessageStatus.DELIVERED, is_ai_generated=True),
            Message(conversation_id=conv2.id, direction=MessageDirection.INBOUND, content="CloudSync ke baare mein jaankari chahiye", status=MessageStatus.DELIVERED),
            Message(conversation_id=conv2.id, direction=MessageDirection.OUTBOUND, content="Namaste Priya! CloudSync Business Suite hamaara enterprise collaboration platform hai. Isme project management, file sharing, aur team communication features hain. Kya aap kisi specific feature ke baare mein jaanna chahti hain?", status=MessageStatus.DELIVERED, is_ai_generated=True),
        ]
        for msg in messages:
            session.add(msg)

        # Create sample lead
        lead = Lead(
            contact_id=contact1.id,
            conversation_id=conv1.id,
            name="Rahul Kumar",
            city="Mumbai",
            product_interest="SmartHome Hub Pro",
            status="qualified",
        )
        session.add(lead)

        # Create default settings
        default_settings = [
            Setting(key="business_name", value="Acme Technologies", category="general", description="Business display name"),
            Setting(key="greeting_message", value="Hello! Welcome to Acme Technologies. How can I help you today?", category="messaging", description="Default greeting message"),
            Setting(key="fallback_message", value="I'm sorry, I couldn't understand that. Could you please rephrase?", category="messaging", description="Fallback message when AI can't respond"),
            Setting(key="ai_tone", value="professional and friendly", category="ai", description="AI response tone"),
            Setting(key="max_ai_retries", value="2", category="ai", description="Max AI retry attempts"),
            Setting(key="business_hours_start", value="09:00", category="business", description="Business hours start"),
            Setting(key="business_hours_end", value="18:00", category="business", description="Business hours end"),
            Setting(key="auto_handoff_enabled", value="true", category="handoff", description="Enable automatic handoff on low confidence"),
        ]
        for setting in default_settings:
            session.add(setting)

        await session.commit()
        print("Seed data created successfully!")
        print("  Admin: admin@example.com / admin123456")
        print("  Operator: operator@example.com / operator123456")
        print("  Analyst: analyst@example.com / analyst123456")


if __name__ == "__main__":
    asyncio.run(seed())
