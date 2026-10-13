from datetime import datetime
import hashlib
from schemas.scheme import SchemeRecord

class SchemeNormalizer:
    @staticmethod
    def normalize(raw_data: dict) -> SchemeRecord:
        """
        Takes raw scraped data from the website crawler and normalizes it 
        into the canonical Pydantic SchemeRecord model, handling missing fields 
        and generating a unique scheme ID.
        """
        # Generate a unique deterministic hash ID based on the scheme name
        scheme_name = raw_data.get("scheme_name_en", "Unknown Scheme")
        scheme_id = hashlib.md5(scheme_name.encode("utf-8")).hexdigest()[:12]
        
        # Track missing fields explicitly as required by the specification
        missing = []
        for field in ["eligibility_criteria", "benefits_amount", "required_documents"]:
            if not raw_data.get(field):
                missing.append(field)

        return SchemeRecord(
            scheme_id=scheme_id,
            scheme_name_en=scheme_name,
            scheme_name_ta=raw_data.get("scheme_name_ta"),
            department=raw_data.get("department", "Tamil Nadu Government"),
            category=raw_data.get("category", "General Welfare"),
            description=raw_data.get("description", "Not available in the retrieved official sources"),
            eligibility_criteria=raw_data.get("eligibility_criteria", ["Not available in the retrieved official sources"]),
            beneficiary_category=raw_data.get("beneficiary_category", ["General Citizens"]),
            income_condition=raw_data.get("income_condition"),
            age_condition=raw_data.get("age_condition"),
            benefits_amount=raw_data.get("benefits_amount", "Not available in the retrieved official sources"),
            subsidy_percentage=raw_data.get("subsidy_percentage"),
            required_documents=raw_data.get("required_documents", ["Not available in the retrieved official sources"]),
            application_procedure=raw_data.get("application_procedure", "Not available in the retrieved official sources"),
            application_portal=raw_data.get("application_portal"),
            offline_location=raw_data.get("offline_location"),
            deadlines=raw_data.get("deadlines"),
            go_references=raw_data.get("go_references", []),
            helpline_details=raw_data.get("helpline_details"),
            source_url=raw_data.get("source_url", ""),
            publication_date=raw_data.get("publication_date"),
            last_verified_timestamp=datetime.utcnow().isoformat(),
            extraction_confidence=raw_data.get("extraction_confidence", 1.0),
            missing_fields=missing
        )