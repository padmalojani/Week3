from neo4j import GraphDatabase

class SchemeGraphManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_scheme_relations(self, record: dict):
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Department {name: $department})
                MERGE (s:Scheme {id: $scheme_id, name: $name})
                MERGE (d)-[:IMPLEMENTS]->(s)
                
                FOREACH (ben IN $beneficiaries :
                    MERGE (b:Beneficiary {category: ben})
                    MERGE (s)-[:BENEFITS]->(b)
                )
                
                FOREACH (doc IN $documents :
                    MERGE (rd:RequiredDocument {name: doc})
                    MERGE (s)-[:REQUIRES_DOCUMENT]->(rd)
                )
            """,
            department=record["department"],
            scheme_id=record["scheme_id"],
            name=record["scheme_name_en"],
            beneficiaries=record.get("beneficiary_category", []),
            documents=record.get("required_documents", []))

    def query_graph(self, cypher_query: str, parameters: dict = None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result]