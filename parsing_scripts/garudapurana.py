import json
import argparse
import re

def parse_verses(input_path, output_path, category="Purana", book="Garudapurana"):
    """
    Read the Garuḍapurāṇa text file and convert it to JSONL format.
    Each verse is converted into a JSON object with relevant metadata.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip header up to # Text
    if "# Header" in content:
        parts = content.split("# Text", 1)
        if len(parts) > 1:
            content = parts[1].strip()

    # Split into blocks by blank lines
    blocks = [blk.strip() for blk in content.split('\n\n') if blk.strip()]

    # Pattern to extract kanda, section, verse: garp_<kanda>,<sarga>.<verse>
    ref_pattern = re.compile(r'garp_(\d+),(\d+)\.(\d+)')

    with open(output_path, 'w', encoding='utf-8') as out:
        for blk in blocks:
            combined = ' '.join(line.strip() for line in blk.splitlines())
            m = ref_pattern.search(combined)
            if not m:
                continue
            kanda, sarga, verse = m.groups()
            # Remove all reference markers
            quote = re.sub(r'//.*?//', '', combined)
            quote = quote.replace('/', '').strip()

            position = f"Kanda {kanda}, Sarga {sarga}, Verse {verse}"
            record = {
                "quote": quote,
                "category": category,
                "book": book,
                "position": position
            }
            out.write(json.dumps(record, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Garudapurana text file into JSONL format."
    )
    parser.add_argument('--input', default="data/garudapurana.txt", help="Input text file path")
    parser.add_argument('--output', default="data/garudapurana.jsonl", help="Output JSONL file path")
    args = parser.parse_args()
    parse_verses(args.input, args.output)
