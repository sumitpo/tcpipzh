import re
from pathlib import Path
import tempfile
import sys

def replace_rfc_references(file_path):
    """
    Replace [RFCxxxx], ［RFCxxxx］ with \\href{https://www.rfc-editor.org/info/rfcxxxx}{RFCxxxx}
    in a LaTeX file, while ignoring already replaced hrefs and modifying the file in-place.
    """
    # Pattern to identify already replaced hrefs
    href_pattern = re.compile(r'\\href\{https://www\.rfc-editor\.org/rfc/rfc\d+\}\{[RFC\d+]\}')
    
    # Pattern to match RFC references not already in href format
    rfc_pattern = re.compile(r'([\[［])RFC(\d+)([\]］])')

    replacement_count = 0
    
    # Create a temporary file for safe writing
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp_file:
        with open(file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                # Split the line into parts that are either hrefs or other text
                parts = []
                last_end = 0
                for match in href_pattern.finditer(line):
                    parts.append(line[last_end:match.start()])  # Text before href
                    parts.append(match.group())                # The href itself
                    last_end = match.end()
                parts.append(line[last_end:])                  # Remaining text
                
                # Process only the non-href parts
                processed_parts = []
                for part in parts:
                    if href_pattern.fullmatch(part):
                        processed_parts.append(part)  # Keep hrefs as-is
                    else:
                        replacement_count += 1
                        # Replace RFC references in non-href parts
                        processed_parts.append(
                            rfc_pattern.sub(
                                lambda m: r'\href{https://www.rfc-editor.org/rfc/rfc' + 
                                m.group(2) + r'}{[RFC' + m.group(2) + r']}',
                                part
                            )
                        )
                
                tmp_file.write(''.join(processed_parts))
        
        # Get the temporary file path
        temp_path = tmp_file.name
    
    # Replace the original file with the temporary file
    Path(temp_path).replace(file_path)
    return replacement_count

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replace_rfc.py input.tex")
        sys.exit(1)
    
    input_file = sys.argv[1]
    replace_count = replace_rfc_references(input_file)
    print(f"{replace_count} RFC references replaced in {input_file} (modified in-place)")