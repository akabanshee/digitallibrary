from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import mimetypes
import os
from fastapi import HTTPException

def combine_author_name(first_name: str, last_name: str) -> str:
    """
    Combines first name and last name into a single full name.
    
    Args:
        first_name (str): Author's first name.
        last_name (str): Author's last name.

    Returns:
        str: Full name in the format "FirstName LastName".
    """
    return f"{first_name} {last_name}"

def upload_file_to_azure(container_client, file, filename: str) -> str:
    """
    Uploads a file to Azure Blob Storage and returns the file URL.

    Args:
        container_client: The container client for the Azure Blob Storage container.
        file: The file-like object to be uploaded.
        filename: The name to save the file as in Azure Blob Storage.

    Returns:
        str: The URL of the uploaded file.
    """
    try:
        # Get the blob client for the file
        blob_client = container_client.get_blob_client(filename)

        # Upload the file
        blob_client.upload_blob(file, overwrite=True)

        # Return the file URL
        return blob_client.url
    except Exception as e:
        raise RuntimeError(f"Failed to upload file to Azure: {e}")


def generate_download_link_with_sas(blob_name: str, expiry_minutes: int = 15, content_type: str = "application/octet-stream") -> str:
    try:
        account_name = "basakdigitalibary"
        container_name = "pdf-container"
        account_key = os.getenv("AZURE_ACCOUNT_KEY")

        if not account_key:
            raise RuntimeError("Azure account key is missing from environment variables.")

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes),
            start=datetime.utcnow() - timedelta(minutes=1),
            content_type=content_type
        )

        blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        return f"{blob_url}?{sas_token}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate SAS token for blob '{blob_name}': {e}")



def is_pdf(file_name: str) -> bool:
    """
    Validates whether the given file is a PDF based on its file extension.

    Args:
        file_name (str): The name of the file.

    Returns:
        bool: True if the file is a PDF, False otherwise.
    """
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type == "application/pdf"
