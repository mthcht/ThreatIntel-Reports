# Optimized Python script to use ripgrep (rg) https://github.com/BurntSushi/ripgrep/releases for keyword search in text files with --update functionality
# put the ripgrep binary in the same directory
import os
import json
import sys
import subprocess
import platform

# Specify the directory containing your Intel Reports
intel_reports_dir = os.path.abspath("Intel Reports")
# Directory for the search results
search_results_dir = "search_results"
os.makedirs(search_results_dir, exist_ok=True)

def search_keyword_with_ripgrep(keyword):
    keyword = keyword.lower()
    results = []
    rg_command = "rg.exe" if platform.system() == "Windows" else "rg"

    try:
        command = [
            rg_command, "-i", "--json", "--fixed-strings", keyword, intel_reports_dir
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        stdout, stderr = process.communicate()

        if process.returncode != 0 and stderr:
            print(f"Error occurred while running ripgrep: {stderr}")
            return results

        for line in stdout.splitlines():
            try:
                data = json.loads(line)
                if data['type'] == 'match':
                    file_path = data['data']['path']['text']
                    line_number = data['data']['line_number']
                    full_context = data['data']['lines']['text'].strip()
                    
                    # Limit to 50 characters before and after the match
                    match_start = data['data']['submatches'][0]['start']
                    match_end = data['data']['submatches'][0]['end']
                    start = max(match_start - 50, 0)
                    end = min(match_end + 50, len(full_context))
                    limited_context = f"...{full_context[start:end]}..."

                    # Check if a link file exists
                    link_path = os.path.join(os.path.dirname(file_path), 'link.md')
                    original_link = ""
                    if os.path.exists(link_path):
                        with open(link_path, "r", encoding="utf-8", errors='ignore') as link_file:
                            original_link = link_file.read().strip()

                    result = {
                        "keyword": keyword,
                        "file": os.path.relpath(file_path, intel_reports_dir),
                        "line_number": line_number,
                        "context": limited_context,
                        "original_link": original_link
                    }
                    results.append(result)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Exception occurred: {e}")

    return results


def log_results(keyword, results, overwrite=False):
    keyword_file_path = os.path.join(search_results_dir, f"{keyword}.json")

    if not overwrite:
        try:
            if os.path.exists(keyword_file_path):
                with open(keyword_file_path, "r", encoding="utf-8") as keyword_file:
                    data = json.load(keyword_file)
            else:
                data = []
        except json.JSONDecodeError:
            data = []
        data.extend(results)
    else:
        data = results  # Overwrite mode - replace existing data

    with open(keyword_file_path, "w", encoding="utf-8") as keyword_file:
        json.dump(data, keyword_file, indent=2)


def search_multiple_keywords(keywords, update_mode=False):
    for keyword in keywords:
        results = search_keyword_with_ripgrep(keyword)
        if results:
            log_results(keyword, results, overwrite=update_mode)
            current_file = None
            for result in results:
                if result['file'] != current_file:
                    if current_file:
                        print("-" * 40)
                    current_file = result['file']
                    print(f"File: {result['file']}")
                    if result['original_link']:
                        print(f"Original Link: {result['original_link']}")
                    print("-" * 40)
                print(f"Line {result['line_number']}: {result['context']}")


def main():
    if '--update' in sys.argv:
        # Update mode: use each .json filename as a keyword to re-search and overwrite files
        keywords = [os.path.splitext(filename)[0] for filename in os.listdir(search_results_dir) if filename.endswith('.json')]
        search_multiple_keywords(keywords, update_mode=True)
    else:
        # Normal mode: search for specified keywords
        if len(sys.argv) > 1:
            keywords = [arg for arg in sys.argv[1:] if arg != "--update"]
        else:
            keywords = input("Enter keywords to search (separated by commas): ").strip().split(',')
            keywords = [keyword.strip() for keyword in keywords if keyword.strip()]

        if not keywords:
            print("Please enter at least one valid keyword.")
            return

        search_multiple_keywords(keywords)


if __name__ == "__main__":
    main()
