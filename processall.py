"""
A script to process the receipts and card statements for reimbursements and generate a
PDF with the necessary information.

Example:

    python processall.py \
            --dir path/to/directory/
"""

import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


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
    name: str,
    date: str,
    description: str,
    n_receipts: int,
    cad: float,
    other_currency: float = None,
    comments: str = None,
):
    # Write markdown file
    markdown = Path(f"{name}.md")
    pdf = Path(f"{name}.pdf")
    if markdown.exists():
        now = str(int(datetime.now().timestamp()))
        markdown = Path(f"{name}_{now}.md")
        pdf = Path(f"{name}_{now}.pdf")
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
    os.system(f"pandoc {markdown.name} -o {pdf.name}")


def main(args):
    """
    Main method of the script.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments
    """
    print_args(args)


if __name__ == "__main__":
    parser = ArgumentParser()
    _, override_args = parser.parse_known_args()
    parser = add_args(parser)
    args = parser.parse_args()
    main(args)

    ### DEBUG ###
    process_item(
        name="hotel",
        date="20/03/2026",
        description="Hotel Lagune Barra - Rio de Janeiro",
        n_receipts=1,
        cad=6579.30,
        other_currency="17.89 JPY",
        comments=None,
    )
    ### DEBUG ###

    sys.exit()
