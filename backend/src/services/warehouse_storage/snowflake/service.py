from config.settings import settings
from snowflake.snowpark import Session

class SnowflakeService:
    def __init__(self):
        self.session = self._create_snowflake_session()

    def _create_snowflake_session(self) -> Session:
        connection_parameters = {
            "account": settings.snowflake_account,
            "user": settings.snowflake_user,
            "password": settings.snowflake_password,
            "warehouse": settings.snowflake_warehouse,
            "database": settings.snowflake_database,
            "schema": settings.snowflake_schema,
        }
        if settings.snowflake_rsa_private_key_path:
            with open(settings.snowflake_rsa_private_key_path, "rb") as key_file:
                private_key = key_file.read()
            connection_parameters["private_key"] = private_key
        
        return Session.builder.configs(connection_parameters).create()

