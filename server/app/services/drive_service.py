"""
Google Drive service for OAuth2 and file management
"""
from typing import Optional
import os
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings
from app.exceptions import DriveAccessDenied

logger = logging.getLogger(__name__)

# Scopes for Drive access
SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveService:
    """Google Drive OAuth2 and file management"""

    @staticmethod
    def get_oauth2_flow() -> Flow:
        """
        Create OAuth2 flow for Google Drive using client credentials file
        
        Returns:
            OAuth2 Flow object
        """
        if not os.path.exists(settings.GOOGLE_CLIENT_CREDENTIALS_FILE):
            raise DriveAccessDenied("Client credentials file not found")
        
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_CREDENTIALS_FILE,
            scopes=SCOPES,
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        return flow

    @staticmethod
    def get_authorization_url() -> str:
        """
        Get OAuth2 authorization URL
        
        Returns:
            Authorization URL
        """
        flow = DriveService.get_oauth2_flow()
        auth_url, _state = flow.authorization_url(prompt="consent")
        return auth_url

    @staticmethod
    async def get_credentials_from_code(code: str) -> Credentials:
        """
        Exchange authorization code for credentials
        
        Args:
            code: Authorization code from OAuth2 callback
            
        Returns:
            Credentials object
        """
        try:
            flow = DriveService.get_oauth2_flow()
            flow.fetch_token(code=code)
            return flow.credentials
        except Exception as e:
            logger.error(f"Failed to get credentials: {str(e)}")
            raise DriveAccessDenied()

    @staticmethod
    def save_credentials(credentials: Credentials) -> str:
        """
        Save credentials as JSON string for storage
        
        Args:
            credentials: Credentials object
            
        Returns:
            JSON string of credentials
        """
        return credentials.to_json()

    @staticmethod
    def load_credentials(credentials_json: str) -> Credentials:
        """
        Load credentials from JSON string
        
        Args:
            credentials_json: JSON string of credentials
            
        Returns:
            Credentials object
        """
        return Credentials.from_authorized_user_info(json.loads(credentials_json), SCOPES)

    @staticmethod
    async def list_files(credentials_json: str, folder_id: Optional[str] = None) -> list:
        """
        List files in Drive or specific folder
        
        Args:
            credentials_json: Credentials JSON string (required)
            folder_id: Folder ID (optional)
            
        Returns:
            List of files
        """
        try:
            credentials = DriveService.load_credentials(credentials_json)
            service = build("drive", "v3", credentials=credentials)
            
            query = "'trashed'=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = (
                service.files()
                .list(
                    q=query,
                    pageSize=100,
                    fields="files(id, name, mimeType, createdTime, modifiedTime, size)",
                    orderBy="modifiedTime desc",
                )
                .execute()
            )
            
            return results.get("files", [])
        except HttpError as e:
            logger.error(f"Drive API error: {str(e)}")
            raise DriveAccessDenied()

    @staticmethod
    async def create_folder(credentials_json: str, folder_name: str) -> str:
        """
        Create folder in Drive
        
        Args:
            credentials_json: Credentials JSON string (required)
            folder_name: Folder name
            
        Returns:
            Folder ID
        """
        try:
            credentials = DriveService.load_credentials(credentials_json)
            service = build("drive", "v3", credentials=credentials)
            
            file_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            
            folder = service.files().create(body=file_metadata, fields="id").execute()
            return folder.get("id")
        except HttpError as e:
            logger.error(f"Failed to create folder: {str(e)}")
            raise DriveAccessDenied()

    @staticmethod
    async def get_file_download_url(credentials_json: str, file_id: str) -> str:
        """
        Get download URL for a file
        
        Args:
            credentials_json: Credentials JSON string (required)
            file_id: File ID
            
        Returns:
            Download URL
        """
        try:
            credentials = DriveService.load_credentials(credentials_json)
            service = build("drive", "v3", credentials=credentials)
            
            # Get file metadata
            file = service.files().get(fileId=file_id, fields="webContentLink").execute()
            return file.get("webContentLink")
        except HttpError as e:
            logger.error(f"Failed to get download URL: {str(e)}")
            raise DriveAccessDenied()
