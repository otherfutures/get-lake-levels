"""
Returns a JSON of USA lake levels on record. 
Can be searched by state (although not all states have lake level records).

Source: https://lakelevels.info
"""

import argparse
import requests
import os
import re
import json
from bs4 import BeautifulSoup
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter


# Feel free to modify if you pref. another
HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"
}


def main():
    # Checks for CLI Args.
    ALL, RESET, SKIP_ASK = cli_args()

    # Gets HTML content
    if ALL:
        html = requests.get("https://www.lakelevels.info/", headers=HEADER)
        state = "All"
    else:
        # Resets defaults at CLI arg.
        if RESET:
            if os.path.isfile("config.json"):
                os.remove("config.json")
                print("Defaults removed!")
            else:
                print(f"Defaults could not be reset: config.json missing!")

        # Checks for default settings
        if not os.path.isfile("config.json"):
            state, url = pick_state(SKIP_ASK)
        else:
            with open("config.json", "r") as f:
                state, url = (json.load(f)).popitem()

        html = requests.get(url, headers=HEADER)

    if html.status_code != 200:
        print(f"Status: {html.status_code} — Try code again\n")
        print(f"Error: {html.content}")
        quit()

    # Calls function to scrape the Beautiful Soup parsed webpage
    table_scraper(BeautifulSoup(html.content, "html.parser"), state)


def cli_args():
    """Usage ex.: python.py lake_levels.py -a"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Get lake level info for all states on record",
    )
    parser.add_argument(
        "-r",
        "--reset",
        action="store_true",
        default=False,
        help="Reset default settings",
    )
    parser.add_argument(
        "-s",
        "--skip_ask",
        action="store_true",
        default=False,
        help="Skip asking user whether to save defaults",
    )

    args = parser.parse_args()

    return (
        args.all,
        args.reset,
        args.skip_ask,
    )


def pick_state(SKIP_ASK):
    """Returns request URL via user input for US state"""
    STATES = [
        "Alabama",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Florida",
        "Georgia",
        "Illinois",
        "Indiana",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nevada",
        "New Mexico",
        "New York",
        "North Carolina",
        "Oklahoma",
        "Oregon",
        "South Carolina",
        "Tennessee",
        "Texas",
        "Utah",
        "Virginia",
        "West Virginia",
        "Wisconsin",
    ]
    word_completer = FuzzyWordCompleter(STATES)

    # Get state from CLI user input
    while True:
        user_input = prompt(f"Enter state:\n", completer=word_completer)
        if user_input in STATES:
            state_name = user_input.replace(" ", "-")
            if not SKIP_ASK:
                save_defaults(user_input, state_name)
            return user_input, f"https://www.lakelevels.info/USA/{state_name}"
        else:
            print(f"{user_input} not found.")


def save_defaults(user_input, state_name):
    """Creates JSON of user settings (i.e. the state & the request URL)"""
    while True:
        ask = (
            input("Would you like to save this state as your default? (y/n) ")
            .strip()
            .lower()
        )
        if ask == "y":
            user_state = {}
            user_state[user_input] = f"https://www.lakelevels.info/USA/{state_name}"

            # Write the above dict. to a JSON
            with open("config.json", "w") as f:
                json.dump(user_state, f, indent=4)

            print("Default settings JSON created!")

            return
        elif ask == "n":
            return
        else:
            print("Invalid entry, please enter y or n.")


def table_scraper(soup, state):
    """
    Scrapes the lake level table & writes formatted info. to CSV;
    Calls another func. to write the info to JSON
    """

    # Keeps line breaks by replacing <br>
    br_tags = soup.find_all("br")
    for br_tag in br_tags:
        br_tag.replace_with(" ")

    # Beautiful Soup finds table & rows
    table = soup.find("table", {"style": "margin-top:15px;"})
    table_headers = table.find_all("th", {"bgcolor": "#CCCCCC"})
    rows = table.find_all("tr", {"bgcolor": "#ffffff"})

    data = {}
    with open(f"{state} Lake Data.csv", "w") as f:
        # Write the headers to the file
        header_list = [a_header.text.strip() for a_header in table_headers]
        f.write(", ".join(header_list).replace("\n", ""))

        # Write the data for each row to the file
        for row in rows:
            columns = row.find_all("td")
            column_list = [
                column.text.strip()
                .replace("\n", "")
                .replace("\xa0", "")
                .replace("&nbsp;", " ")
                .replace(",", "")
                for column in columns
            ]
            # Removes weird & huge whitespace b/w Date & Time
            column_list[-1] = " ".join(column_list[-1].split())
            f.write("\n" + ", ".join(column_list))

            # Make JSON
            make_json(data, state, header_list, column_list)

    return


def make_json(data, state, header_list, all_columns):
    # Extract the lake name from the first column
    lake_name = all_columns[0].replace("({})".format(state), "").strip()

    lake = {}

    for i, head in enumerate(header_list[1:]):
        lake[head] = all_columns[i + 1]

    # Adds state to data dict. if not preexisting
    if state not in data and state != "All":
        data[state] = {}

    # Add the current iter. lake to the dict.
    if state != "All":
        data[state][lake_name] = lake

    else:
        # RegEx pattern for state abbrev. (i.e. w/n parantheses)
        pattern = r"\((.*?)\)"

        state_list = []

        ## Split the table into rows and loop through each row
        for row in "\n".join(all_columns).split("\n"):
            # Extract the values in parentheses from the first column
            match = re.search(pattern, row)
            if match:
                # Split on whitespace & add ea. abbrev. to the list
                state_list += match.group(1).split()

        for state in state_list:
            state_fullname = state_abbreviations(state)

            if state_fullname not in data:
                data[state_fullname] = {}

            data[state_fullname][lake_name] = lake

        if data:  # Just in case data's empty (altho. unlikely)
            with open("lakes.json", "w") as f:
                json.dump(data, f, indent=4)

    return


def state_abbreviations(abbreviation):
    """Quickly converts state abbreviations to the state's full name"""
    state_abbreviations = {
        "AK": "Alaska",
        "AL": "Alabama",
        "AR": "Arkansas",
        "AS": "American Samoa",
        "AZ": "Arizona",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DC": "District of Columbia",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "GU": "Guam",
        "HI": "Hawaii",
        "IA": "Iowa",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "MA": "Massachusetts",
        "MD": "Maryland",
        "ME": "Maine",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MO": "Missouri",
        "MP": "Northern Mariana Islands",
        "MS": "Mississippi",
        "MT": "Montana",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "NE": "Nebraska",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NV": "Nevada",
        "NY": "New York",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TT": "Trust Territories",
        "TX": "Texas",
        "UT": "Utah",
        "VA": "Virginia",
        "VI": "Virgin Islands",
        "VT": "Vermont",
        "WA": "Washington",
        "WI": "Wisconsin",
        "WV": "West Virginia",
        "WY": "Wyoming",
    }
    return state_abbreviations[abbreviation]


if __name__ == "__main__":
    main()
