import json
import argparse
import re

def parse_verses(input_path, output_path, category="Epic, Mahabharata", book="Bhagavad Gita"):
    """
    Read the Bhagavad Gita text file and convert it to JSONL format.
    Each verse is converted into a JSON object with relevant metadata.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip header section
    if "# Header" in content:
        content = content.split("# Text")[1].strip()

    # Split into blocks by blank lines
    blocks = [blk.strip() for blk in content.split('\n\n') if blk.strip()]

    # Patterns for chapter markers and verse numbers
    chapter_pattern = re.compile(r'^bhg\s+(\d+)\.\d+', re.IGNORECASE)
    verse_pattern = re.compile(r'\|\|(\d+)\|\|')

    current_chapter = None

    with open(output_path, 'w', encoding='utf-8') as out:
        for blk in blocks:
            # Update chapter when encountering a chapter marker
            chap_match = chapter_pattern.match(blk)
            if chap_match:
                current_chapter = chap_match.group(1)
                continue

            # Skip blocks without verse delimiter
            if '||' not in blk:
                continue

            # Combine lines into one string
            combined = ' '.join(line.strip() for line in blk.splitlines())

            # Extract verse number
            verse_match = verse_pattern.search(combined)
            if not verse_match:
                continue
            verse_id = verse_match.group(1)

            # Clean the verse text by removing markers
            quote = verse_pattern.sub('', combined)
            quote = quote.replace('|', '').strip()

            # Build record
            position = f"{current_chapter}.{verse_id}"
            record = {
                "quote": quote,
                "category": category,
                "book": book,
                "position": position
            }
            out.write(json.dumps(record, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Bhagavad Gita text file into JSONL format."
    )
    parser.add_argument('--input', default="data/bhagwvadgita.txt", help="Input text file path")
    parser.add_argument('--output', default="data/bhagwvadgita.jsonl", help="Output JSONL file path")
    args = parser.parse_args()
    parse_verses(args.input, args.output)
