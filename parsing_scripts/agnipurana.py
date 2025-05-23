import json
import argparse

def parse_verses(input_path, output_path, category="Purana", book="Agnipurana"):
    """
    Read the Agni Purana text file and convert it to JSONL format.
    Each verse is converted into a JSON object with relevant metadata.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip the header section
    if "# Header" in content:
        content = content.split("# Text")[1].strip()

    # Split into chapters
    chapters = content.split(":ś atha")[1:]  # Skip the first empty part
    
    with open(output_path, 'w', encoding='utf-8') as out:
        for chapter in chapters:
            # Get chapter number
            chapter_num = chapter.split("'dhyāyaḥ")[0].strip().split()[0]
            
            # Get verses
            verses = chapter.split("\n")
            current_verse = []
            
            for line in verses:
                line = line.strip()
                
                # Skip chapter markers and footnotes
                if line.startswith(":") or not line:
                    continue
                
                # If line contains verse marker (//)
                if "//" in line:
                    # Add this line to current verse
                    current_verse.append(line)
                    
                    # Process complete verse
                    verse_text = " ".join(current_verse)
                    
                    # Extract verse number and text
                    try:
                        verse_id = verse_text.split("ap_")[1].split()[0]
                        # Clean the verse text by removing markers and IDs
                        clean_text = " ".join([part.split("//")[0] for part in current_verse])
                        clean_text = " ".join(clean_text.split())  # normalize whitespace
                        
                        # Remove verse IDs and clean up
                        clean_text = clean_text.split("/ap_")[0].strip()
                        
                        record = {
                            "quote": clean_text,
                            "category": category,
                            "book": book,
                            "position": f"Chapter {chapter_num}, Verse {verse_id}"
                        }
                        
                        out.write(json.dumps(record, ensure_ascii=False) + '\n')
                    except IndexError:
                        pass  # Skip malformed verses
                    
                    current_verse = []
                else:
                    current_verse.append(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Agni Purana text file into JSONL format."
    )
    parser.add_argument('--input', default="data/agnipurana.txt", help="Input text file path")
    parser.add_argument('--output', default="data/agnipurana.jsonl", help="Output JSONL file path")
    args = parser.parse_args()
    
    parse_verses(args.input, args.output)
