"""
A script to process the receipts and card statements for reimbursements and generate a
PDF with the necessary information.

Example:

    python processall.py \
            --dir sampledir/ \
            --verbose 2 \
"""

import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def add_args(parser):
    """
    Adds command-line arguments to parser

    Returns:
        argparse.Namespace: the parsed arguments
    """
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to directory containing the receipts, card statements and CSV "
        "files with the expenses.",
        required=True,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        type=int,
        default=1,
        help="Level of verbosity, the higher the more verbose.",
    )
    parser.add_argument(
        "--keeptmp",
        default=False,
        action="store_true",
        help="If used, the auxiliary files generated during the programme execution"
        "are not deleted.",
    )
    return parser


def print_args(args):
    """
    Prints the arguments

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments
    """
    print("Arguments:")
    darg = vars(args)
    max_k = max([len(k) for k in darg]) + 1
    for k in darg:
        print(f"\t{k:{max_k}}: {darg[k]}")


def process_item(
    basedir: str,
    keeptmp: bool,
    name: str,
    date: str,
    description: str,
    n_receipts: int,
    cad: float,
    other_currency: float = None,
    comments: str = None,
):
    # Find PDF files related to the item being processed
    pdfs_item = Path(basedir).glob(f"{name}*.pdf")

    # Find payment PDF file related to the item being processed
    card_pdf = [el for el in Path(basedir).glob(f"{name}*_card.pdf")]
    # If no PDF file is find, search PNG file
    if len(card_pdf) == 0:
        card_png = [el for el in Path(basedir).glob(f"{name}*_card.png")]
        if len(card_png) == 0:
            raise RuntimeError(f"No card payment file found for item {name}!")
        if len(card_png) > 1:
            raise RuntimeError(f"Multiple card payment files found for item {name}!")
        # Convert PNG file to PDF
        card_png = card_png[0]
        card_pdf = card_png.with_suffix(".pdf")
        os.system(f"convert {str(card_png.absolute())} {str(card_pdf.absolute())}")
    else:
        if len(card_pdf) > 1:
            raise RuntimeError(f"Multiple card payment files found for item {name}!")
        card_pdf = card_pdf[0]

    # Create markdown file with summary information
    markdown = Path(basedir) / f"{name}.md"
    pdf = Path(basedir) / f"{name}.pdf"
    if markdown.exists():
        now = str(int(datetime.now().timestamp()))
        markdown = Path(basedir) / f"{name}_{now}.md"
        pdf = Path(basedir) / f"{name}_{now}.pdf"
    if pdf.exists():
        raise RuntimeError(f"File {pdf.name} exists!")
    with open(markdown, "w") as f:
        f.write("---\n")
        f.write("header-includes:\n")
        f.write("- \\pagenumbering{gobble}\n")
        f.write("---\n")
        f.write("\n")
        f.write(f"# {description}\n")
        f.write("\n")
        f.write(f"- Date : {date}\n")
        f.write("- Dépense : {:.2f} CAD".format(cad))
        if other_currency:
            f.write(f" ({other_currency})\n")
        else:
            f.write("\n")
        f.write(f"- Nombre de reçus : {n_receipts}\n")
        if comments:
            f.write(f"- Commentaires : {comments}\n")
    # Convert markdown file to PDF
    os.system(f"pandoc {str(markdown.absolute())} -o {str(pdf.absolute())}")

    # Concatenate all PDFs related to the item being processed

    # Clean up files
    if not keeptmp:
        markdown.unlink()
        pdf.unlink()
        card_pdf.unlink()


def process_section(basedir: str, name: str, keeptmp: bool = False, verbose: int = 0):
    # Read CSV of section
    basedir = Path(basedir) / name
    csv = basedir / f"{name}.csv"
    df = pd.read_csv(csv, index_col=False)
    # Replace empty strings and NaN with None
    df = df.replace({"": None, np.nan: None})
    if verbose > 0:
        print(f"Processing {name} from {str(csv.absolute())}")
    # Process each row (expense item) of the CSV
    for row in df.iterrows():
        if verbose > 1:
            print(f"\tProcessing {row[1].description}")
        process_item(basedir, keeptmp, **row[1].to_dict())


def main(args):
    """
    Main method of the script.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments
    """
    if args.verbose > 0:
        print_args(args)

    # Process accommodation
    process_section(args.dir, "accommodation", args.keeptmp, args.verbose)
    # Process transport
    process_section(args.dir, "transport", args.keeptmp, args.verbose)
    # Process misc
    process_section(args.dir, "misc", args.keeptmp, args.verbose)


if __name__ == "__main__":
    parser = ArgumentParser()
    _, override_args = parser.parse_known_args()
    parser = add_args(parser)
    args = parser.parse_args()
    main(args)
    sys.exit()
