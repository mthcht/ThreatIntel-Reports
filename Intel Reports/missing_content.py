import os

# Initialize counters and lists
count = 0
link_md_without_txt = []
link_md_contents = []

# Loop through all directories and subdirectories
for root, dirs, files in os.walk('.'):
    # Check if link.md exists in the directory
    if 'link.md' in files:
        txt_files = [file for file in files if file.endswith('.txt')]
        # If there are no .txt files in the same directory
        if not txt_files:
            count += 1
            link_md_path = os.path.join(root, 'link.md')
            link_md_without_txt.append(link_md_path)
            # Read the contents of link.md
            with open(link_md_path, 'r') as f:
                link_md_contents.append(f.read())

# Print the result
print(f"Number of directories with link.md but without a .txt file: {count}")
print("Paths to link.md without a .txt file:")
for path in link_md_without_txt:
    print(path)

# Save the contents of each link.md file
#print("Contents of each link.md without a .txt file:")
#for content in link_md_contents:
#    print(content)
