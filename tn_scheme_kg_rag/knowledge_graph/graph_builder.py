from knowledge_graph.neo4j_client import neo4j_client
from schemas.scheme import SchemeRecord
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    @staticmethod
    def upsert_scheme_graph(scheme: SchemeRecord):
        """
        Takes a normalized SchemeRecord and creates or merges nodes and relationships 
        in the Neo4j Knowledge Graph.
        """
        query = """
        MERGE (d:Department {name: $department})
        MERGE (s:Scheme {id: $scheme_id})
        SET s.name_en = $name_en, 
            s.name_ta = $name_ta, 
            s.description = $description, 
            s.source_url = $source_url
        MERGE (d)-[:IMPLEMENTS]->(s)
        
        FOREACH (beneficiary IN $beneficiaries |
            MERGE (b:Beneficiary {name: beneficiary})
            MERGE (s)-[:BENEFITS]->(b)
        )
        
        FOREACH (doc IN $documents |
            MERGE (rd:RequiredDocument {name: doc})
            MERGE (s)-[:REQUIRES]->(rd)
        )
        """
        params = {
            "department": scheme.department,
            "scheme_id": scheme.scheme_id,
            "name_en": scheme.scheme_name_en,
            "name_ta": scheme.scheme_name_ta or "",
            "description": scheme.description,
            "source_url": scheme.source_url,
            "beneficiaries": scheme.beneficiary_category,
            "documents": scheme.required_documents
        }
        
        try:
            neo4j_client.run_query(query, params)
        except Exception as e:
            logger.error(f"Error writing scheme {scheme.scheme_name_en} to Neo4j: {e}")