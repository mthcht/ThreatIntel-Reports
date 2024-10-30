# Modified Python script to use ripgrep (rg) for keyword search in text files
import os
import json
import sys
import subprocess
import platform

# Specify the directory containing your Intel Reports
intel_reports_dir = os.path.abspath("Intel Reports")
# Directory for the search results
search_results_dir = "search_results"

# Ensure the search results directory exists
os.makedirs(search_results_dir, exist_ok=True)

def search_keyword_with_ripgrep(keyword, existing_results):
    keyword = keyword.lower()
    results = []

    try:
        # Determine the appropriate ripgrep command based on the operating system
        rg_command = "rg"
        if platform.system() == "Windows":
            rg_command = "rg.exe"

        # Run ripgrep to search for the keyword in the .txt files
        command = [
            rg_command, "-i", "--json", "--fixed-strings", keyword, f"{intel_reports_dir}"
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        stdout, stderr = process.communicate()

        if process.returncode != 0 and stderr:
            print(f"Error occurred while running ripgrep: {stderr}")
            return results

        # Process each JSON line output by ripgrep
        for line in stdout.splitlines():
            try:
                data = json.loads(line)
                if data['type'] == 'match':
                    file_path = data['data']['path']['text']
                    relative_file_path = os.path.relpath(file_path, intel_reports_dir)
                    line_number = data['data']['line_number']
                    context = data['data']['lines']['text'].strip()
                    link_path = os.path.join(os.path.dirname(file_path), 'link.md')
                    original_link = ""

                    if os.path.exists(link_path):
                        with open(link_path, "r", encoding="utf-8", errors='ignore') as link_file:
                            original_link = link_file.read().strip()

                    result = {
                        "keyword": keyword,
                        "file": relative_file_path,
                        "line_number": line_number,
                        "context": context,
                        "original_link": original_link
                    }

                    # Check if the result already exists based on specific fields
                    if not any(r['file'] == result['file'] and 
                               r['line_number'] == result['line_number'] and 
                               r['context'] == result['context'] for r in existing_results):
                        results.append(result)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Exception occurred: {e}")

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
        results = search_keyword_with_ripgrep(keyword, existing_results)
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
