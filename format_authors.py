import argparse
import logging
import os.path
import re
import time

"""
***Assumptions***:
- only one author or affiliation exists per line
- author and affiliations are never multi-line
"""

time_prog_start = time.time()


def is_valid_file(arg):
    """Function that validates if file argument is a valid file"""
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError(f"The file {arg} does not exist!")
    else:
        return arg


# Initial configuration for logging and arg parser
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(module)s.%(funcName)s(%(lineno)d) - %(message)s",
    level=logging.CRITICAL,
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Simple program that tries to identify unique author affiliations in .tex file and formats them more tidily"
)
parser.add_argument(
    "file_in", help="Path to authors file to be parsed", type=is_valid_file,
)
parser.add_argument(
    "file_out", help="Path to file to be written",
)
parser.add_argument(
    "--debug",
    help="Set looging to DEBUG, for many many many messages to be displayed",
    required=False,
    action="store_true",
)


# Main function
def main():
    args = parser.parse_args()  # Get passed arguments

    # Extract them
    file_in = vars(args)["file_in"]
    file_out = vars(args)["file_out"]

    # Enable debugging if asked
    if vars(args)["debug"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug(f"File in: {file_in}")
    logger.debug(f"File out: {file_out}")

    affiliations_dict = (
        {}
    )  # Empty dict to store affiliations in as keys and for each key, a list of authors
    all_authors = []
    re_author = re.compile(r"\\author\{(?P<author>.+[^{])\}")  # Author extraction RegEx
    re_affiliation = re.compile(r"\\affiliation\{(?P<affiliation>.+)\}")

    curr_line = 0
    last_author = None
    last_affiliation_unique_id = 0

    # Open input file
    with open(file_in, "r") as f:
        # Read it
        for line in f:
            curr_line += 1
            # Skip commented lines
            if line.startswith("%"):
                logger.debug(f"Skipping commented line {curr_line}")
                continue

            # Filter inline comments
            comment_start = line.find("%")
            if comment_start >= 0:
                logger.debug(f"Found comment at {curr_line}:{comment_start}")
                comment_start += 1
            else:
                # Set comment_start to end of current line
                comment_start = len(line)

            # Look for author in current line
            m = re_author.search(line, endpos=comment_start)
            if m is not None:
                logger.debug(
                    f'Found author "{m["author"]} at {curr_line}:{m.start("author")}'
                )
                if m["author"] not in all_authors:
                    all_authors.append(m["author"])
                last_author = m["author"]
                # print(m.start("author"))
            else:
                m = re_affiliation.search(line, endpos=comment_start)
                if m is not None:
                    logger.debug(f'Found affiliation "{m["affiliation"]}')
                    if last_author is not None:
                        # Initialize an authors list for current affiliation
                        if m["affiliation"] not in affiliations_dict:
                            last_affiliation_unique_id += 1
                            affiliations_dict[m["affiliation"]] = {
                                "id": last_affiliation_unique_id,
                                "authors": [],
                            }
                        if (
                            last_author
                            not in affiliations_dict[m["affiliation"]]["authors"]
                        ):
                            affiliations_dict[m["affiliation"]]["authors"].append(
                                last_author
                            )
    logger.debug(f"Resulting dictionary: {affiliations_dict}")
    logger.info(
        f"Found a total of {len(all_authors)} unique authors and {len(affiliations_dict.keys())} unique affiliations"
    )

    # Write new file with correct format
    logger.info(f"Writing re-formatted authors and affiliations to {file_out}")
    with open(file_out, "w+") as f:
        # Loop across all unique authors and look for them in the authors
        # of each affiliation
        for author in all_authors:
            aff_ids = []
            # aff_desc = []
            # Loop in all key value pairs in affiliations_dict
            for k, v in affiliations_dict.items():

                if author in v["authors"]:
                    if v["id"] not in aff_ids:
                        aff_ids.append(v["id"])
                        # aff_desc.append(k)
            if len(aff_ids) < 1:
                logger.error(f"{author} has no affiliations!")
            f.writelines(f"\\author{[id for id in aff_ids]}{{{author}}}\n")

        f.writelines("\n")

        # for aff in aff_desc:
        for k in affiliations_dict.keys():
            f.writelines(f"\\affiliation[{affiliations_dict[k]['id']}]{{{k}}}\n")


main()
time_prog_stop = time.time()
logger.debug(f"Execution of program took {time_prog_stop - time_prog_start} s")
