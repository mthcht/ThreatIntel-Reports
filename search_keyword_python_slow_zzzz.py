# Python script to search through all .txt files in the command line
import os
import re
import json
import sys

# Specify the directory containing your Intel Reports
intel_reports_dir = os.path.abspath("Intel Reports")
# Directory for the search results
search_results_dir = "search_results"

# Ensure the search results directory exists
os.makedirs(search_results_dir, exist_ok=True)

def search_keyword(keyword, existing_results):
    keyword = keyword.lower()
    results = []
    total_files = sum(len(files) for _, _, files in os.walk(intel_reports_dir))
    files_processed = 0

    for root, dirs, files in os.walk(intel_reports_dir):
        # Check for the presence of any "content.txt", "txt_content_from_pdf_extracted.txt", or "content_*.txt" files and "link.md"
        if any(f.startswith("content") and f.endswith(".txt") for f in files) and 'link.md' in files:
            # Gather all matching content files
            content_files = [f for f in files if f == 'content.txt' or f == 'txt_content_from_pdf_extracted.txt' or (f.startswith("content_") and f.endswith(".txt"))]
            
            # Process each matching content file
            for content_file in content_files:
                file_path = os.path.join(root, content_file)
                # Make file path relative to intel_reports_dir
                relative_file_path = os.path.relpath(file_path, intel_reports_dir)
                link_path = os.path.join(root, 'link.md')
                original_link = ""

                if os.path.exists(link_path):
                    with open(link_path, "r", encoding="utf-8", errors='ignore') as link_file:
                        original_link = link_file.read().strip()

                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    lines = f.readlines()
                    for line_number, line in enumerate(lines, start=1):
                        match = re.search(rf'\b{re.escape(keyword)}\b', line, re.IGNORECASE)
                        if match:
                            start = max(match.start() - 50, 0)
                            end = min(match.end() + 50, len(line))
                            context = line[start:end].strip()
                            result = {
                                "keyword": keyword,
                                "file": relative_file_path,  # Use relative path
                                "line_number": line_number,
                                "context": context,
                                "original_link": original_link
                            }
                            
                            # Check if the result already exists based on specific fields
                            if not any(r['file'] == result['file'] and 
                                       r['line_number'] == result['line_number'] and 
                                       r['context'] == result['context'] for r in existing_results):
                                results.append(result)
                
                # Update and display the progress
                files_processed += 1
                progress_percentage = (files_processed / total_files) * 100
                print(f"\rProgress: {progress_percentage:.2f}% ({files_processed}/{total_files} files processed)", end="")

    print("\n")  # Move to a new line after progress is complete
    return results


def log_results(keyword, results):
    # Define the path for the individual keyword file
    keyword_file_path = os.path.join(search_results_dir, f"{keyword}.json")
    
    # Load existing data for the specific keyword
    try:
        if os.path.exists(keyword_file_path):
            with open(keyword_file_path, "r", encoding="utf-8") as keyword_file:
                data = json.load(keyword_file)
        else:
            data = []
    except json.JSONDecodeError:
        data = []

    # Append new results
    data.extend(results)

    # Save updated data to the dedicated keyword file
    with open(keyword_file_path, "w", encoding="utf-8") as keyword_file:
        json.dump(data, keyword_file, indent=2)

def search_multiple_keywords(keywords):
    for keyword in keywords:
        # Load existing results for this keyword
        keyword_file_path = os.path.join(search_results_dir, f"{keyword}.json")
        try:
            with open(keyword_file_path, "r", encoding="utf-8") as log_file:
                existing_results = json.load(log_file)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_results = []
        
        # Perform the search and log results
        results = search_keyword(keyword, existing_results)
        if results:
            log_results(keyword, results)
            current_file = None
            for result in results:
                if result['file'] != current_file:
                    if current_file is not None:
                        print("-" * 40)
                    current_file = result['file']
                    print(f"File: {result['file']}")
                    if result['original_link']:
                        print(f"Original Link: {result['original_link']}")
                    print("-" * 40)
                print(f"Line {result['line_number']}: ...{result['context']}...")

def main():
    if len(sys.argv) > 1:
        keywords = sys.argv[1:]
    else:
        keywords = input("Enter keywords to search (separated by commas): ").strip().split(',')
        keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
    
    if not keywords:
        print("Please enter at least one valid keyword.")
        return

    search_multiple_keywords(keywords)

if __name__ == "__main__":
    main()
