import json
import argparse
import re

def parse_verses(input_path, output_path, category="Epic, Ramayana", book="Ramayana"):
    """
    Read the Rāmāyaṇa text file and convert it to JSONL format.
    Each verse is converted into a JSON object with metadata.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip header up to # Text
    if "# Header" in content:
        content = content.split("# Text")[1].strip()

    # Split into verse blocks by blank lines
    blocks = [blk.strip() for blk in content.split('\n\n') if blk.strip()]

    # Pattern to extract reference R_<kanda>,<sarga>.<verse>
    ref_pattern = re.compile(r'R_(\d+),(\d+)\.(\d+)')

    with open(output_path, 'w', encoding='utf-8') as out:
        for blk in blocks:
            combined = ' '.join(line.strip() for line in blk.splitlines())
            m = ref_pattern.search(combined)
            if not m:
                continue
            kanda, sarga, verse = m.groups()
            # remove reference
            quote = ref_pattern.sub('', combined).strip()
            # build position
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
        description="Convert Rāmāyaṇa text file into JSONL format."
    )
    parser.add_argument('--input', default="data/ramayana.txt", help="Input text file path")
    parser.add_argument('--output', default="data/ramayana.jsonl", help="Output JSONL file path")
    args = parser.parse_args()
    parse_verses(args.input, args.output)
