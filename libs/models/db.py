from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# Define the base class for declarative models
Base = declarative_base()
load_dotenv()

table_context_dict: dict[str, str] = {
    "clients": """
        This table stores detailed information about each client, including their identity, contact information, demographics, and financial profile. \
        Clients are the primary entities who perform transactions in the system.

        Key Columns:

        first_name, last_name: The full name of the client.
        date_of_birth: The client's date of birth.
        email, phone: Contact information.
        id_type, id_number: Government-issued identification details (e.g., passport, national ID).
        street_address, city, state, postal_code, country: Full address details of the client.
        annual_income, income_currency: Financial details including annual income and its currency.
        nationality: The client's country of citizenship.
        
        Relationships:
        - Linked to the Transaction table via client_id.

        Query Usage:

        Client Lookup: Retrieve full profiles of clients using identifiers such as email, ID number, or name.
        Financial Analysis: Analyze clients based on income brackets or nationality.
        Audit Trails: Link client records with their transactions for compliance or fraud checks.
    """,
    "transactions": """
        This table records all financial transactions associated with each client. Each entry represents a single transaction and includes monetary \
        details, type, and timing.

        Key Columns:

        transaction_number: A unique identifier for each transaction.
        client_id: Foreign key referencing the client involved in the transaction.
        transaction_type: The type/category of the transaction (e.g., deposit, withdrawal).
        amount: The transaction amount.
        currency: The ISO 3-letter currency code used in the transaction.
        transaction_date: The date and time when the transaction occurred.

        Relationships:
        - Linked to the Client table via client_id.

        Query Usage:

        Transaction History: Retrieve all transactions for a specific client.
        Financial Reporting: Aggregate transactions by type, currency, or date for reporting and analysis.
        Fraud Detection: Monitor transaction volumes and frequency per client for anomalies.
    """,
}



class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Personal Details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    
    # Identification
    id_type = Column(String(50), nullable=True)
    id_number = Column(String(50), nullable=True)
    
    # Address
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Income
    annual_income = Column(Numeric(15, 2))
    income_currency = Column(String(3))
    
    # Nationality
    nationality = Column(String(100))
    
    # Relationship
    transactions = relationship("Transaction", back_populates="client")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_number = Column(String(50), unique=True, nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=True)
    transaction_type = Column(String(50),nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)  # ISO currency code
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    client = relationship("Client", back_populates="transactions")