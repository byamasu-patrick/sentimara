from typing import Dict, List

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import sessionmaker


class DBEventHandler:
    def __init__(
        self, db_uri: str, sqlite_session, condition_to_function_map: dict[str, str]
    ):
        """Initialize the database handler with a connection engine."""
        self.condition_to_function_map = condition_to_function_map
        self.engine: Engine = create_engine(db_uri)
        # Create a session
        self.sqlite_session = sqlite_session

        # Create a session for PostgreSQL
        # TODO: Variable name "SessionPG" doesn't conform to snake_case naming style
        SessionPG = sessionmaker(bind=self.engine)
        self.pg_session = SessionPG()

    def register_tables(self, tables: List[str], conn: Connection) -> None:
        """Register tables with the necessary triggers."""

        for table in tables:
            # Check if the trigger exists for the table.
            check_trigger_sql = text(
                """
                SELECT 1 FROM pg_trigger WHERE tgname = :trigger_name
            """
            ).bindparams(trigger_name=f"llm_integration_trigger_{table}")

            # Drop the trigger if it exists.
            drop_trigger_sql = text(
                f"DROP TRIGGER IF EXISTS llm_integration_trigger_{table} ON {table};"
            )

            # Create a new trigger for the table.
            create_trigger_sql = text(
                f"""
                CREATE TRIGGER llm_integration_trigger_{table} 
                AFTER INSERT OR UPDATE ON {table}
                FOR EACH ROW EXECUTE FUNCTION notify_trigger();
            """
            )

            trigger_exists = conn.execute(check_trigger_sql).scalar()

            if trigger_exists:
                # If trigger exists, replace it with a new one.
                print(f"Trigger exists for {table}. Replacing...")
                conn.execute(drop_trigger_sql)
                conn.commit()
                conn.execute(create_trigger_sql)
                conn.commit()
            else:
                print(f"No trigger found for {table}. Creating...")
                # If no trigger exists, create a new one.
                conn.execute(create_trigger_sql)
                conn.commit()

        print("All triggers set up successfully.")

    def create_trigger_function(self, table_lists: List[str]) -> None:
        """Creates or replaces a PostgreSQL trigger function."""

        function_sql = text(
            """
            CREATE OR REPLACE FUNCTION notify_trigger() RETURNS trigger AS $$
            BEGIN
                PERFORM pg_notify('llm_integration_channel', TG_TABLE_NAME || ',' || NEW.id::text || ',' || TG_OP);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """
        )

        try:
            with self.engine.connect() as conn:
                conn.execute(function_sql)
                conn.commit()
                self.register_tables(table_lists, conn)

        except Exception as e:
            print(f"Error while creating function: {e}")

    def check_condition_and_execute_function(self, table_name, id: int) -> None:
        function_name = self.condition_to_function_map.get(table_name)

        if function_name:
            # Get the function object using getattr
            self.condition_to_function_map[table_name](
                self.pg_session, self.sqlite_session, id
            )
        else:
            print(f"No matching function for condition: {table_name}")

    def process_upsert_action(self, payload: Dict[str, int]):
        """Processes payload to replicate changes."""
        for key, value in payload.items():
            print("*************************************************************")
            print("Processing the migration for {}...".format(key))
            self.check_condition_and_execute_function(key, value)
            print("ID: {}".format(value))
            print("Migration for {} has completed!".format(key))
            print("*************************************************************")

    def listen_to_changes(self, conn: Connection):
        """Listens to database changes and processes them."""

        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                table_name, record_id, action = notify.payload.split(",")

                if action == "INSERT":
                    print(f"New record inserted in {table_name} with ID {record_id}")
                    # Handle insert action
                    self.process_upsert_action(
                        {
                            table_name: record_id,
                        }
                    )
                elif action == "UPDATE":
                    print(f"Record in {table_name} with ID {record_id} was updated")
                    # Handle update action
                    self.process_upsert_action(
                        {
                            table_name: record_id,
                        }
                    )

    def establish_connection(self):
        """Establishes a database connection and starts listening for changes."""

        with self.engine.connect() as connection:
            conn = connection.connection  # Extract raw psycopg2 connection
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute("LISTEN llm_integration_channel;")
            self.listen_to_changes(conn)
