from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
import vertexai

# Create a RAG Corpus, Import Files, and Generate a response


PROJECT_ID = "ramesh-ai-project-457712"
display_name = "pdlc-rag-corpus"
# paths = ["https://drive.google.com/file/d/123", "gs://my_bucket/my_files_dir"]  # Supports Google Cloud Storage and Google Drive Links

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location="us-central1")


def process_rag_corpus(bucket_name: str) -> None:

    SOURCE_GCS_BUCKET = f"gs://{bucket_name}/"
    print(f"Source Bucket: {SOURCE_GCS_BUCKET}")
    
    # Check if corpus already exists
    try:
        # List existing corpora and check if our corpus exists
        corpora = rag.list_corpora()
        existing_corpus = None
        
        for corpus in corpora:
            if corpus.display_name == display_name:
                existing_corpus = corpus
                print(f"Found existing corpus: {corpus.name}")
                break
        
        if existing_corpus is None:
            # Create RagCorpus if it doesn't exist
            print(f"Creating new corpus: {display_name}")
            
            # Configure embedding model, for example "text-embedding-005".
            embedding_model_config = rag.RagEmbeddingModelConfig(
                vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                    publisher_model="publishers/google/models/text-embedding-005"
                )
            )

            rag_corpus = rag.create_corpus(
                display_name=display_name,
                backend_config=rag.RagVectorDbConfig(
                    rag_embedding_model_config=embedding_model_config
                ),
            )
            print(f"Created new corpus: {rag_corpus.name}")
        else:
            rag_corpus = existing_corpus
            print(f"Using existing corpus: {rag_corpus.name}")

        # Import Files to the RagCorpus
        print(f"Importing files from {SOURCE_GCS_BUCKET}")
        response = rag.import_files(
            rag_corpus.name,
            paths=[SOURCE_GCS_BUCKET],            
            # Optional
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(
                    chunk_size=512,
                    chunk_overlap=100,
                ),
            ),
            max_embedding_requests_per_min=1000,  # Optional
            import_result_sink="gs://pdlc-rag-results/rag_results.ndjson",  
        )
        print(f"Import response: skipped {response.skipped_rag_files_count} files")
        print(f"Imported {response.imported_rag_files_count} files.")
        print("Files imported successfully")
        
    except Exception as e:
        print(f"Error processing RAG corpus: {str(e)}")
        raise


