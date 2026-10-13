from ingestion.pipeline import SchemeIngestionPipeline

def test_pipeline_hash():
    pipeline = SchemeIngestionPipeline(db_path="./data/test_metadata.db")
    h1 = pipeline.compute_hash("Test Scheme")
    h2 = pipeline.compute_hash("Test Scheme")
    assert h1 == h2