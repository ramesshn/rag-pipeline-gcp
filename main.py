from cloudevents.http import CloudEvent
import functions_framework
from google.cloud import storage
from rag.rag_pipline import process_rag_corpus
import time
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track processed files and prevent duplicate processing
_processed_files = set()

@functions_framework.cloud_event
def pdlc_rag(cloud_event: CloudEvent) -> tuple:
    """Triggered by a change in a storage bucket."""
    
    try:
        data = cloud_event.data
        
        event_id = cloud_event["id"]
        event_type = cloud_event["type"]
        
        raw_bucket = data["bucket"]
        filename = data["name"]
        metageneration = data["metageneration"]
        time_created = data["timeCreated"]
        updated = data["updated"]
        
        processing_bucket = "pdlc-process-bucket"
        
        logger.info(f"Event ID: {event_id}")
        logger.info(f"Event Type: {event_type}")
        logger.info(f"Bucket: {raw_bucket}")
        logger.info(f"File: {filename}")
        logger.info(f"Metageneration: {metageneration}")
        logger.info(f"Created: {time_created}")
        logger.info(f"Updated: {updated}")
        
        file_identifier = f"{raw_bucket}/{filename}/{metageneration}"
        
        if file_identifier in _processed_files:
            logger.warning(f"File {filename} already processed, skipping...")
            return event_id, event_type, raw_bucket, filename
        
        if event_type != "google.cloud.storage.object.v1.finalized":
            logger.info(f"Ignoring event type: {event_type}")
            return event_id, event_type, raw_bucket, filename
        
        if filename.startswith('.') or filename.endswith('.tmp'):
            logger.info(f"Skipping temporary/system file: {filename}")
            return event_id, event_type, raw_bucket, filename
        
        _processed_files.add(file_identifier)
        logger.info(f"Processing file: {filename}")
        
        storage_client = storage.Client()
        source_bucket = storage_client.bucket(raw_bucket)
        destination_bucket = storage_client.bucket(processing_bucket)
        
        source_blob = source_bucket.blob(filename)
        
        if not source_blob.exists():
            logger.error(f"File {filename} does not exist in {raw_bucket}")
            return event_id, event_type, raw_bucket, filename
        
        destination_blob = destination_bucket.blob(filename)
        if destination_blob.exists():
            logger.warning(f"File {filename} already exists in processing bucket")
            source_blob.delete()
            logger.info(f"Deleted duplicate {filename} from {raw_bucket}")
            return event_id, event_type, raw_bucket, filename
        
        new_blob = source_bucket.copy_blob(source_blob, destination_bucket, filename)
        logger.info(f"Successfully copied {filename} to {processing_bucket}")
        
        source_blob.delete()
        logger.info(f"Successfully deleted {filename} from {raw_bucket}")
        
        time.sleep(2)
        
        logger.info(f"Starting RAG processing for {filename}")
        process_rag_corpus(processing_bucket, filename)
        logger.info(f"Completed RAG processing for {filename}")
        
    except Exception as e:
        logger.exception(f"Error in pdlc_rag function: {str(e)}")
        logger.error("Function completed with error - not retrying to prevent loops")
        return (
            event_id if 'event_id' in locals() else "unknown",
            event_type if 'event_type' in locals() else "unknown",
            raw_bucket if 'raw_bucket' in locals() else "unknown",
            filename if 'filename' in locals() else "unknown"
        )

    return event_id, event_type, raw_bucket, filename
