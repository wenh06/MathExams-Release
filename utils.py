import argparse
import re
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility script for MathExams.")
    parser.add_argument(
        "--find-overriden-symbols", action="store_true", help="Find overridden symbols in the MathExams LaTeX files."
    )
    args = parser.parse_args()

    if args.find_overriden_symbols:
        symbols = "|".join(Path("overriden-symbols.txt").read_text().splitlines())
        pattern = f"\\\\(?:{symbols})(?![\\*a-zA-Z])"
        found = False
        files = list(Path("content").rglob("*.tex"))
        print(f"{len(files)} content files found.")
        for file in files:
            content = file.read_text().splitlines()
            found_lines = []
            for line_idx, line in enumerate(content):
                if re.search(pattern, line):
                    if not found:
                        print("Found overridden symbols:")
                    found_lines.append((line_idx + 1, line.strip()))
                    found = True
            if found_lines:
                print(f"File: {file}")
                for line_num, line in found_lines:
                    print(f"  Line {line_num}: {line}")
                print("-" * 80)
        if not found:
            print("No overridden symbols found in the content files.")
            exit(0)
        else:
            exit(1)
