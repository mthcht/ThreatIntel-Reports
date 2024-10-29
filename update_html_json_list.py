import os
import re
import json

# Paths
json_directory = 'search_results'
html_file_path = 'index.html'
intel_reports_directory = 'Intel Reports'

def count_reports():
    # Initialize the counter
    count = 0

    # Traverse directories and count valid report folders
    for root, dirs, files in os.walk(intel_reports_directory):
        if 'link.md' in files:
            txt_files = [file for file in files if file.endswith('.txt')]
            for txt_file in txt_files:
                if os.path.dirname(os.path.join(root, 'link.md')) == os.path.dirname(os.path.join(root, txt_file)):
                    count += 1
                    break
    return count

def update_html_file():
    # Initialize the keyword to file mapping
    keyword_to_file_map = {}

    # Read each JSON file in the directory
    for file in os.listdir(json_directory):
        if file.endswith('.json'):
            file_path = os.path.join(json_directory, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    # Extract keywords from the data
                    for entry in data:
                        keyword = entry.get('keyword')
                        if keyword:
                            if keyword in keyword_to_file_map:
                                if file not in keyword_to_file_map[keyword]:
                                    keyword_to_file_map[keyword].append(file)
                            else:
                                keyword_to_file_map[keyword] = [file]
            except Exception as e:
                print(f"Error reading {file}: {e}")

    # Convert the keyword_to_file_map to a string representation suitable for JavaScript
    keyword_to_file_map_str = json.dumps(keyword_to_file_map, indent=4)

    # Get the total report count
    report_count = count_reports()

    # Read the HTML file content
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Update the keywordToFileMap variable in the HTML
    keyword_map_pattern = r'const keywordToFileMap = \{.*?\};'
    new_keyword_map_content = f'const keywordToFileMap = {keyword_to_file_map_str};'
    updated_html_content = re.sub(keyword_map_pattern, new_keyword_map_content, html_content, flags=re.DOTALL)

    # Define and replace the report count under the title
    report_count_pattern = r'<div class="report-count".*?>.*?</div>'
    report_count_html = f'<div class="report-count" style="font-size: 0.9rem; color: #90a955;">Total Reports: {report_count}</div>'
    if re.search(report_count_pattern, updated_html_content):
        updated_html_content = re.sub(report_count_pattern, report_count_html, updated_html_content, flags=re.DOTALL)
    else:
        # Insert if not already present, right below the title container
        title_insert_pattern = r'(<div class="title-container.*?</h1>)'
        updated_html_content = re.sub(title_insert_pattern, rf'\1\n{report_count_html}', updated_html_content, flags=re.DOTALL)

    # Write back the modified content
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_html_content)

    print("HTML file updated successfully with the keywordToFileMap and total report count.")

# Run the update function
update_html_file()
