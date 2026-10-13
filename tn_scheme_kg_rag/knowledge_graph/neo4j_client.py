from neo4j import GraphDatabase
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI, 
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query: str, parameters: dict = None):
        """
        Executes a Cypher query against the configured Neo4j database.
        """
        if not self.driver:
            raise ConnectionError("Neo4j driver is not initialized. Check your credentials in .env.")
        
        with self.driver.session(database=settings.NEO4J_DATABASE) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# Global instance for easy importing across modules
neo4j_client = Neo4jClient()