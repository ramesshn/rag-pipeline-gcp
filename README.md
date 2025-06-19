# RAG Pipeline

A Retrieval-Augmented Generation (RAG) pipeline built on Google Cloud Platform that automatically processes documents uploaded to Cloud Storage and creates searchable knowledge bases using Vertex AI.

## Overview

This project implements an event-driven RAG pipeline that:
- Monitors Google Cloud Storage buckets for new document uploads
- Automatically processes documents using Vertex AI RAG services
- Creates and manages RAG corpora for efficient document retrieval
- Enables semantic search and question-answering capabilities

## Architecture

```
Cloud Storage → Cloud Function → Vertex AI RAG → Vector Database
     ↓              ↓               ↓              ↓
  Document       Event           Embedding      Searchable
   Upload       Trigger         Generation      Corpus
```

## Features

- **Automatic Document Processing**: Triggered by Cloud Storage events
- **Smart Corpus Management**: Reuses existing corpora to avoid duplicates
- **Configurable Chunking**: Customizable document chunking parameters
- **Error Handling**: Comprehensive error handling and logging
- **Scalable**: Handles multiple documents and large corpora

## Prerequisites

- Google Cloud Platform account
- Python 3.9+
- Vertex AI API enabled
- Cloud Functions API enabled
- Cloud Storage bucket with event notifications configured

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-pipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up authentication:
```bash
gcloud auth application-default login
```

## Configuration

1. Update the project configuration in `rag/rag_pipline.py`:
```python
PROJECT_ID = "your-project-id"
display_name = "your-corpus-name"
```

2. Configure the embedding model and chunking parameters as needed.

## Deployment

Follow this link for Cloud storage trigger to Cloud Run function:
https://cloud.google.com/run/docs/tutorials/trigger-functions-storage


### Deploy Cloud Function

gcloud run deploy pdlc-rag-events `
      --source . `
      --function pdlc_rag `
      --base-image python313 `
      --region us-central1

### Deploy EventArc trigger

use the default compute servcie account:

gcloud eventarc triggers create pdlc-rag-trigger  `
    --location=us-central1 `
    --destination-run-service=pdlc-rag-events  `
    --destination-run-region=us-central1 `
    --event-filters="type=google.cloud.storage.object.v1.finalized" `
    --event-filters="bucket=pdlc-rag-bucket" `
    --service-account=SERVICE-ACCOUNT

### Set up IAM Permissions

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/run.invoker

gcloud projects add-iam-policy-binding PROJECT_ID  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com   --role=roles/eventarc.eventReceiver

gcloud projects add-iam-policy-binding PROJECT_ID  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com   --role=roles/aiplatform.user

gcloud projects add-iam-policy-binding PROJECT_ID `
   --member="serviceAccount:service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com" `
   --role='roles/pubsub.publisher'
   
 gcloud projects add-iam-policy-binding PROJECT_ID `
   --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-vertex-rag.iam.gserviceaccount.com" `
   --role='roles/storage.objectCreator'


## Usage

1. **Upload Documents**: Upload documents to your configured Cloud Storage bucket
2. **Monitor Processing**: Check Cloud Function logs for processing status
3. **Query the Corpus**: Use the generated corpus for RAG applications

### Supported File Types

- PDF documents
- Text files (.txt, .md)
- Microsoft Word documents (.docx)
- And other formats supported by Vertex AI

## API Reference

### Main Functions

#### `process_rag_corpus(bucket_name: str)`

Processes documents from a Cloud Storage bucket and updates the RAG corpus.

**Parameters:**
- `bucket_name`: Name of the Cloud Storage bucket containing documents

**Returns:**
- None

**Raises:**
- Exception: If corpus creation or file import fails

## Configuration Options

### Chunking Configuration

```python
chunking_config=rag.ChunkingConfig(
    chunk_size=512,        # Size of each text chunk
    chunk_overlap=100,     # Overlap between chunks
)
```

### Embedding Model

```python
embedding_model_config = rag.RagEmbeddingModelConfig(
    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        publisher_model="publishers/google/models/text-embedding-005"
    )
)
```

## Monitoring

### Logs


```

### Metrics

Check import results in the configured result sink bucket for detailed processing information.

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure service account has proper IAM roles
2. **Corpus Not Found**: Check if corpus creation succeeded
3. **Import Failures**: Verify file formats and bucket accessibility

### Debug Commands

List existing corpora:
```bash
# Use Vertex AI console or SDK to list corpora
```

Check bucket contents:
```bash
gsutil ls -la gs://your-bucket-name/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check Google Cloud documentation for Vertex AI RAG
- Review Cloud Functions troubleshooting guides

## Changelog

### v1.0.0
- Initial release
- Basic RAG corpus management
- Cloud Storage event triggering
- Document chunking and embedding

