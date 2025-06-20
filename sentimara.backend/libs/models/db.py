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
        - Linked to the Transaction table via client_number.

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
        client_number: Foreign key referencing the client involved in the transaction.
        transaction_type: The type/category of the transaction (e.g., deposit, withdrawal).
        amount: The transaction amount.
        currency: The ISO 3-letter currency code used in the transaction.
        transaction_date: The date and time when the transaction occurred.

        Relationships:
        - Linked to the Client table via client_number.

        Query Usage:

        Transaction History: Retrieve all transactions for a specific client.
        Financial Reporting: Aggregate transactions by type, currency, or date for reporting and analysis.
        Fraud Detection: Monitor transaction volumes and frequency per client for anomalies.
    """,
}
