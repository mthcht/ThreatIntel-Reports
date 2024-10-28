import os
import re
import time

# Regex pattern to detect URLs
url_pattern = re.compile(r'(https?://\S+)')

def is_pdf(file_path):
    """Check if a file is a PDF by reading its signature."""
    try:
        with open(file_path, 'rb') as f:
            return f.read(4) == b'%PDF'
    except:
        return False

def get_unique_name(path, base_name, extension):
    """Generate a unique file name only if a file with the desired name exists."""
    new_path = os.path.join(path, f"{base_name}{extension}")
    counter = 1
    while os.path.exists(new_path):
        new_path = os.path.join(path, f"{base_name}_{counter}{extension}")
        counter += 1
    return new_path

def rename_file_with_retry(old_path, new_path, retries=3, delay=1):
    """Attempt to rename a file with retries to handle PermissionError."""
    for attempt in range(retries):
        try:
            os.rename(old_path, new_path)
            print(f'Renamed: {old_path} to {new_path}')
            return True
        except PermissionError:
            print(f"PermissionError on {old_path}. Retry {attempt + 1}/{retries}")
            time.sleep(delay)
    print(f"Failed to rename {old_path} after {retries} attempts.")
    return False

def process_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Determine the appropriate name based on file content
            if is_pdf(file_path):
                target_name = 'content.pdf'
                new_name = get_unique_name(root, 'content', '.pdf') if file != target_name else file_path
            
            else:
                # Read file content to determine text type
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    # Check for HTML content with multiple possible starts
                    first_line = lines[0].strip().lower()
                    if len(lines) == 1 and (first_line.startswith("<!doctype html>") or 
                                            first_line.startswith("<html")):
                        target_name = 'content.txt'
                        new_name = get_unique_name(root, 'content', '.txt') if file != target_name else file_path
                    
                    elif len(lines) == 1 and re.search(url_pattern, lines[0]):
                        target_name = 'link.md'
                        new_name = get_unique_name(root, 'link', '.md') if file != target_name else file_path
                        
                    elif len(lines) > 1:
                        target_name = 'content.txt'
                        new_name = get_unique_name(root, 'content', '.txt') if file != target_name else file_path
                        
                    else:
                        continue  # Skip if file doesn't match any criteria
                except:
                    continue  # Skip files that can’t be read as text

            # Rename the file only if it doesn’t already match the target name
            if os.path.basename(file_path) != target_name:
                rename_file_with_retry(file_path, new_name)

# Example usage
process_files(r'C:\Users\mthcht\Documents\GitHub\ThreatIntel-Reports\Intel Reports')
