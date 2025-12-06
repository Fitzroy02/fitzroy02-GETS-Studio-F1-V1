"""
Media Loader Module for GETS Compliance Studio
Handles media ingestion with jurisdiction-aware access controls
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
import hashlib


class MediaLoader:
    """
    Media ingestion and preview system with jurisdiction-aware controls.
    Handles video, books, scenarios, trailers, and podcasts with author attribution.
    """
    
    def __init__(self, config_dir: str = "."):
        """
        Initialize the Media Loader.
        
        Args:
            config_dir: Directory containing loader_config.yaml
        """
        self.config_dir = Path(config_dir)
        self.loader_config = self._load_loader_config()
        self.ingested_items = []
        
    def _load_loader_config(self) -> Dict:
        """Load media loader configuration from YAML."""
        loader_file = self.config_dir / "loader_config.yaml"
        if not loader_file.exists():
            raise FileNotFoundError(f"Loader config not found at {loader_file}")
        
        with open(loader_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _detect_media_type(self, filename: str) -> str:
        """
        Detect media type from filename extension.
        
        Args:
            filename: Media file name
            
        Returns:
            Media type string (video, book, scenario, trailer, podcast)
        """
        ext = Path(filename).suffix.lower()
        
        # Extension to media type mapping
        type_map = {
            # Video
            '.mp4': 'video',
            '.avi': 'video',
            '.mov': 'video',
            '.mkv': 'video',
            '.webm': 'video',
            
            # Books
            '.pdf': 'book',
            '.epub': 'book',
            '.mobi': 'book',
            '.txt': 'book',
            '.md': 'book',
            
            # Scenarios
            '.json': 'scenario',
            '.yaml': 'scenario',
            '.yml': 'scenario',
            
            # Trailers
            '.trailer.mp4': 'trailer',
            '.trailer.mov': 'trailer',
            
            # Podcasts
            '.mp3': 'podcast',
            '.wav': 'podcast',
            '.m4a': 'podcast',
            '.ogg': 'podcast',
        }
        
        # Check for trailer in filename
        if 'trailer' in filename.lower():
            return 'trailer'
        
        return type_map.get(ext, 'video')  # Default to video if unknown
    
    def _generate_media_id(self, filename: str, author: str) -> str:
        """Generate unique media ID."""
        content = f"{filename}{author}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def ingest(
        self,
        filename: str,
        author: Optional[str] = None,
        pen_name: Optional[str] = None,
        media_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest media file with author attribution.
        
        Args:
            filename: Media file name or path
            author: Real author name
            pen_name: Author's pen name or alias
            media_type: Override media type detection (video, book, scenario, trailer, podcast)
            metadata: Additional metadata dictionary
            
        Returns:
            Ingestion result dictionary with media ID and status
        """
        # Detect or use provided media type
        if media_type is None:
            media_type = self._detect_media_type(filename)
        
        # Validate media type
        supported_types = list(self.loader_config.get('media_types', {}).keys())
        if media_type not in supported_types:
            raise ValueError(f"Unsupported media type: {media_type}. Must be one of {supported_types}")
        
        # Generate media ID
        media_id = self._generate_media_id(filename, author or pen_name or "anonymous")
        
        # Build ingestion record
        ingestion = {
            'media_id': media_id,
            'filename': filename,
            'media_type': media_type,
            'author': author,
            'pen_name': pen_name,
            'display_name': pen_name if pen_name else author,
            'ingested_at': datetime.now().isoformat(),
            'status': 'ingested',
            'metadata': metadata or {}
        }
        
        # Add to ingested items
        self.ingested_items.append(ingestion)
        
        print(f"✓ Ingested: {filename}")
        print(f"  → Media Type: {media_type}")
        print(f"  → Media ID: {media_id}")
        if author:
            print(f"  → Author: {author}")
        if pen_name:
            print(f"  → Pen Name: {pen_name}")
        
        return ingestion
    
    def preview(self, media_id: Optional[str] = None) -> None:
        """
        Preview ingested media items.
        
        Args:
            media_id: Specific media ID to preview (None = show all)
        """
        if not self.ingested_items:
            print("⚠ No media items ingested yet.")
            return
        
        items_to_show = self.ingested_items
        
        if media_id:
            items_to_show = [item for item in self.ingested_items if item['media_id'] == media_id]
            if not items_to_show:
                print(f"⚠ Media ID not found: {media_id}")
                return
        
        print("\n" + "=" * 70)
        print(f"Media Preview - {len(items_to_show)} item(s)")
        print("=" * 70)
        
        for idx, item in enumerate(items_to_show, 1):
            print(f"\n[{idx}] {item['filename']}")
            print("-" * 70)
            print(f"  Media ID:      {item['media_id']}")
            print(f"  Type:          {item['media_type']}")
            print(f"  Author:        {item.get('author', 'N/A')}")
            print(f"  Pen Name:      {item.get('pen_name', 'N/A')}")
            print(f"  Display Name:  {item.get('display_name', 'N/A')}")
            print(f"  Ingested:      {item['ingested_at']}")
            print(f"  Status:        {item['status']}")
            
            if item.get('metadata'):
                print(f"  Metadata:      {item['metadata']}")
        
        print("\n" + "=" * 70)
    
    def get_jurisdiction_rules(self, media_id: str, profile_name: str) -> Dict:
        """
        Get jurisdiction-specific access rules for media item.
        
        Args:
            media_id: Media item identifier
            profile_name: Jurisdiction profile (e.g., 'UK_OSA_v1')
            
        Returns:
            Access rules dictionary
        """
        # Find media item
        item = next((i for i in self.ingested_items if i['media_id'] == media_id), None)
        if not item:
            raise ValueError(f"Media ID not found: {media_id}")
        
        media_type = item['media_type']
        
        # Get rules from config
        media_types = self.loader_config.get('media_types', {})
        jurisdiction_rules = media_types[media_type].get('controls', {}).get('jurisdiction_rules', {})
        
        if profile_name not in jurisdiction_rules:
            # Return default behavior
            return self.loader_config.get('default_behavior', {}).get('unknown_jurisdiction', {})
        
        return jurisdiction_rules[profile_name]
    
    def check_access(self, media_id: str, profile_name: str, user_age: int) -> Dict:
        """
        Check if user can access media based on jurisdiction and age.
        
        Args:
            media_id: Media item identifier
            profile_name: Jurisdiction profile
            user_age: User's age
            
        Returns:
            Access decision dictionary
        """
        rules = self.get_jurisdiction_rules(media_id, profile_name)
        
        access_status = rules.get('access', 'allowed')
        min_age = rules.get('min_age', 0)
        
        item = next((i for i in self.ingested_items if i['media_id'] == media_id), None)
        media_type = item['media_type'] if item else 'unknown'
        
        if access_status == 'disabled':
            return {
                'allowed': False,
                'reason': f'{media_type} is disabled in this jurisdiction',
                'media_id': media_id,
                'profile': profile_name,
                'rules': rules
            }
        
        if min_age and user_age < min_age:
            return {
                'allowed': False,
                'reason': f'Age requirement not met (requires {min_age}+, user is {user_age})',
                'media_id': media_id,
                'profile': profile_name,
                'rules': rules
            }
        
        status = 'restricted' if access_status == 'restricted' else 'allowed'
        return {
            'allowed': True,
            'status': status,
            'reason': f'Access {status} - all requirements met',
            'media_id': media_id,
            'profile': profile_name,
            'rules': rules
        }
    
    def list_ingested(self) -> List[Dict]:
        """Get list of all ingested media items."""
        return self.ingested_items.copy()
    
    def get_item(self, media_id: str) -> Optional[Dict]:
        """Get specific media item by ID."""
        return next((i for i in self.ingested_items if i['media_id'] == media_id), None)
    
    def clear(self) -> None:
        """Clear all ingested items."""
        count = len(self.ingested_items)
        self.ingested_items.clear()
        print(f"✓ Cleared {count} ingested item(s)")
    
    def __repr__(self) -> str:
        """String representation of the loader."""
        return f"<MediaLoader: {len(self.ingested_items)} item(s) ingested>"


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = MediaLoader()
    
    # Ingest media
    loader.ingest("video.mp4", author="John T. Hope", pen_name="DJ Fitz")
    
    # Preview
    loader.preview()
    
    # Additional examples
    print("\n" + "=" * 70)
    print("Additional Examples")
    print("=" * 70)
    
    # Ingest different media types
    loader.ingest("audiobook.mp3", author="Jane Doe", media_type="podcast")
    loader.ingest("story.pdf", author="Alice Smith", pen_name="A. S. Writer")
    loader.ingest("scenario.json", author="Bob Johnson")
    
    # Preview all
    loader.preview()
    
    # Check access for specific item
    print("\nAccess Check Examples:")
    print("-" * 70)
    
    items = loader.list_ingested()
    if items:
        first_item = items[0]
        
        # Check access for UK user (age 15)
        access_uk = loader.check_access(first_item['media_id'], 'UK_OSA_v1', user_age=15)
        print(f"\nUK (age 15): {access_uk['allowed']} - {access_uk['reason']}")
        
        # Check access for AU user (age 15)
        access_au = loader.check_access(first_item['media_id'], 'AU_Ban_v1', user_age=15)
        print(f"AU (age 15): {access_au['allowed']} - {access_au['reason']}")
