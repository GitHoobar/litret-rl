import os
import argparse
from datasets import DatasetDict, load_dataset


def main(repo_id, token=None):
    # Map of dataset splits or subsets to JSONL files
    data_dir = "data"
    files = {
        "agnipurana": os.path.join(data_dir, "agnipurana.jsonl"),
        "rigveda": os.path.join(data_dir, "rigveda.jsonl"),
        "bhagavadgita": os.path.join(data_dir, "bhagwvadgita.jsonl"),
        "ramayana": os.path.join(data_dir, "ramayana.jsonl"),
        "garudapurana": os.path.join(data_dir, "garudapurana.jsonl"),
    }

    ds_dict = DatasetDict()
    for name, path in files.items():
        print(f"Loading {name} from {path}")
        ds = load_dataset("json", data_files=path, split="train")
        ds_dict[name] = ds

    print(f"Pushing dataset to Hugging Face repo: {repo_id}")
    ds_dict.push_to_hub(repo_id, token=token)
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload JSONL files as an HF Datasets repo.")
    parser.add_argument(
        "--repo_id", default="Rixhabh/sanskrit-literature",
        help="Hugging Face dataset repo ID, e.g. username/dataset-name"
    )
    parser.add_argument(
        "--token", default=None,
        help="HF API token (or set HF_TOKEN env var)"
    )
    args = parser.parse_args()

    token = args.token or os.getenv("HF_TOKEN")
    if token is None:
        print("Warning: No HF token provided. Make sure you're logged in via huggingface-cli.")
    main(args.repo_id, token)
