#!/usr/bin/env python3
"""Script to improve download error handling"""

# Read the file
with open('jira_dc_scanner.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the _download_and_hash_single method
old_method_start = '    def _download_and_hash_single(self, attachment: dict) -> Optional[Tuple[str, str, dict]]:'
old_method_end = '            except:\n                return None'

new_method = '''    def _download_and_hash_single(self, attachment: dict) -> Optional[Tuple[str, str, dict]]:
        """
        Download single file and calculate hash.
        
        Args:
            attachment: Attachment metadata
            
        Returns:
            Tuple of (attachment_id, file_hash, metadata) or None if failed
        """
        attachment_id = attachment['id']
        file_size = attachment['size']
        content_url = attachment['content']
        file_name = attachment.get('filename', 'unknown')
        
        # Skip files that are too large
        if file_size > self.max_file_size:
            self.logger.warning(
                f"Skipping large file: {file_name} "
                f"({self._format_bytes(file_size)})"
            )
            # Use URL hash for large files
            url_hash = StreamingHasher.hash_from_url(content_url)
            return (attachment_id, url_hash, attachment)
        
        try:
            if self.use_content_hash:
                # Download and hash actual content
                response = self.jira_client.download_attachment(
                    content_url,
                    stream=True,
                    timeout=self.timeout
                )
                
                file_hash = StreamingHasher.hash_from_stream(
                    response.iter_content(chunk_size=8192)
                )
            else:
                # Use URL-based hash (faster, less accurate)
                file_hash = StreamingHasher.hash_from_url(content_url)
            
            return (attachment_id, file_hash, attachment)
            
        except requests.exceptions.ChunkedEncodingError as e:
            # Handle "Response ended prematurely" errors
            self.logger.warning(
                f"Download incomplete for {file_name}: {e}. Using URL hash as fallback."
            )
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None
                
        except requests.exceptions.Timeout as e:
            self.logger.warning(
                f"Download timeout for {file_name}: {e}. Using URL hash as fallback."
            )
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None
                
        except Exception as e:
            self.logger.warning(
                f"Download failed for {file_name}: {e}. Using URL hash as fallback."
            )
            # Try URL-based hash as fallback
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None'''

# Find the method
start_idx = content.find(old_method_start)
if start_idx == -1:
    print("ERROR: Could not find _download_and_hash_single method")
    exit(1)

# Find the end of the method (next method definition or class end)
end_search_start = start_idx + len(old_method_start)
end_idx = content.find('\n    def ', end_search_start)
if end_idx == -1:
    end_idx = content.find('\n\n# ===', end_search_start)

# Replace the method
new_content = content[:start_idx] + new_method + content[end_idx:]

# Write back
with open('jira_dc_scanner.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ Improved download error handling")
print("✓ Added specific handling for ChunkedEncodingError and Timeout")
print("✓ Scanner will now continue even if files are unavailable")
