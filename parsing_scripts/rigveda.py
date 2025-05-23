import json
import argparse


def parse_verses(input_path, output_path, category="Veda, Samhita", book="Rigveda"):
    """
    Read a text file of Vedic verses separated by blank lines, each ending with '|| POSITION',
    and write each verse as a JSON object per line in JSONL format. Removes any '|' characters within the verse.
    """
    # Read the entire file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove any triple-quote delimiters
    content = content.replace('"""', '')

    # Split into blocks by two or more newlines
    blocks = [blk.strip() for blk in content.split('\n\n') if blk.strip()]

    with open(output_path, 'w', encoding='utf-8') as out:
        for blk in blocks:
            # Skip blocks without the '||' separator
            if '||' not in blk:
                continue
            # Combine multiple lines into a single string
            combined = ' '.join(line.strip() for line in blk.splitlines())
            # Split into quote text and position
            try:
                quote_part, pos_part = combined.rsplit('||', 1)
            except ValueError:
                continue  # malformed block

            # Clean up quote and position
            quote = quote_part.replace('|', '').strip()
            position = pos_part.strip()

            record = {
                "quote": quote,
                "category": category,
                "book": book,
                "position": position
            }
            # Write as a single JSON line
            out.write(json.dumps(record, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a text file of Vedic verses into JSONL format."
    )
    parse_verses("data/rigveda.txt", "data/rigveda.jsonl")
