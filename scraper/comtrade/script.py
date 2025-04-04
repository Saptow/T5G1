import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

import comtradeapicall

# Create data directory if it doesn't exist
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

# Create country pairs directory
country_pairs_dir = data_dir / "country_pairs"
country_pairs_dir.mkdir(exist_ok=True)

# Set up logging
log_file = data_dir / "error.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Checkpoint file path
checkpoint_file = data_dir / "checkpoint.json"


# Function to get country name from code
def get_country_name(code):
    country_names = {
        "702": "Singapore",
        "156": "China",
        "458": "Malaysia",
        "842": "United_States",
        "344": "Hong_Kong",
        "360": "Indonesia",
        "410": "South_Korea",
        "392": "Japan",
        "764": "Thailand",
        "36": "Australia",
        "704": "Vietnam",
        "699": "India",
        "784": "UAE",
        "608": "Philippines",
        "276": "Germany",
        "251": "France",
        "757": "Switzerland",
        "528": "Netherlands",
    }
    return country_names.get(code, f"Country_{code}")


# Function to save checkpoint
def save_checkpoint(code, code2, year):
    checkpoint = {"code": code, "code2": code2, "year": year}
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint, f)
    print(f"Saved checkpoint: {code} trading with {code2} in {year}")


# Function to load checkpoint
def load_checkpoint():
    if checkpoint_file.exists():
        with open(checkpoint_file, "r") as f:
            checkpoint = json.load(f)
            print(
                f"Resuming from checkpoint: {checkpoint['code']} trading with {checkpoint['code2']} in {checkpoint['year']}"
            )
            return checkpoint
    return None


# Load last checkpoint
checkpoint = load_checkpoint()
resume_from_checkpoint = checkpoint is not None

subscription_key = "52eba4ae292948b690bd77326a9bacb1"  # comtrade api subscription key (from comtradedeveloper.un.org)

# Period from 1994 to 2023
periods = [
    "1994",
    "1995",
    "1996",
    "1997",
    "1998",
    "1999",
    "2000",
    "2001",
    "2002",
    "2003",
    "2004",
    "2005",
    "2006",
    "2007",
    "2008",
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
]

relevantCode = [
    "702",  # Singapore
    "156",  # China
    "458",  # Malaysia
    "842",  # United States
    "344",  # Hong Kong
    "360",  # Indonesia
    "410",  # Republic of Korea
    "392",  # Japan
    "764",  # Thailand
    "36",  # Australia
    "704",  # Viet Nam
    "699",  # India
    "784",  # United Arab Emirates
    "608",  # Philippines
    "276",  # Germany
    "251",  # France
    "757",  # Switzerland
    "528",  # Netherlands
]

# Loop through relevantCode and call getFinalData and getFinalData
for code in relevantCode:
    for code2 in relevantCode:
        if code == code2:
            continue

        # Skip to checkpoint if resuming
        if resume_from_checkpoint:
            if code == checkpoint["code"] and code2 == checkpoint["code2"]:
                resume_from_checkpoint = False
                # Find the year index to resume from and add 1 to start from next year
                year_index = periods.index(checkpoint["year"]) + 1
                if year_index < len(periods):
                    current_periods = periods[year_index:]
                    print(f"Continuing from year {current_periods[0]}")
                else:
                    print(
                        "Checkpoint year was the last year, moving to next country pair"
                    )
                    continue
            else:
                current_periods = periods
                continue
        else:
            current_periods = periods

        for year in current_periods:
            try:
                print(
                    f"\nAttempting to fetch data for {code} trading with {code2} in {year}"
                )

                # Capture stdout to check for error messages
                import sys
                from io import StringIO

                old_stdout = sys.stdout
                result = StringIO()
                sys.stdout = result

                mydf = comtradeapicall.getFinalData(
                    subscription_key,
                    typeCode="C",
                    freqCode="A",
                    clCode="HS",
                    period=year,
                    reporterCode=code,
                    cmdCode="AG6",
                    flowCode="M,X,RX,RM,MIP,XIP,MOP,XOP,MIF,XIF,DX,FM",
                    partnerCode=code2,
                    partner2Code=None,
                    customsCode=None,
                    motCode=None,
                    maxRecords=250000,
                    format_output="JSON",
                    aggregateBy=None,
                    breakdownMode="classic",
                    countOnly=None,
                )

                # Restore stdout and get the captured output
                sys.stdout = old_stdout
                output = result.getvalue()

                # Check if the output contains the quota limit message
                if "Out of call volume quota" in output:
                    print("API quota limit reached. Stopping script.")
                    print(f"Quota message: {output.strip()}")
                    logging.error("Script stopped due to API quota limit")
                    exit(1)

                # Check for various error conditions
                if mydf is None:
                    error_msg = f"No data returned for country {code} trading with {code2} in {year}"
                    print(error_msg)
                    logging.error(error_msg)
                    continue

                if isinstance(mydf, str):
                    if "Out of call volume quota" in mydf or "403" in mydf:
                        print("API quota limit reached. Stopping script.")
                        logging.error("Script stopped due to API quota limit")
                        exit(1)
                    error_msg = f"Unexpected string response: {mydf}"
                    print(error_msg)
                    logging.error(error_msg)
                    continue

                # Try to convert to DataFrame
                try:
                    mydf = pd.DataFrame(mydf)
                except Exception as e:
                    error_msg = f"Failed to convert response to DataFrame for {code} trading with {code2} in {year}: {str(e)}"
                    print(error_msg)
                    logging.error(error_msg)
                    continue

                # Check if DataFrame is empty
                if mydf.empty:
                    error_msg = f"No data returned for country {code} trading with {code2} in {year}"
                    print(error_msg)
                    logging.error(error_msg)
                    continue

                # Add country code and period columns
                mydf["country_code"] = code
                mydf["period"] = year

                # Save to CSV
                output_file = country_pairs_dir / f"{code}_{code2}.csv"

                # If file exists, append without header, otherwise create new file with header
                header = not output_file.exists()
                mydf.to_csv(output_file, mode="a", header=header, index=False)
                print(
                    f"Successfully saved data for {code} trading with {code2} in {year}"
                )

                # Save checkpoint after each successful iteration
                save_checkpoint(code, code2, year)

            except Exception as e:
                error_msg = str(e)
                print(f"Error: {error_msg}")  # Print the full error message
                if "Out of call volume quota" in error_msg:
                    print("API quota limit reached. Stopping script.")
                    logging.error("Script stopped due to API quota limit")
                    exit(1)
                else:
                    print(
                        f"Error processing country {code} trading with {code2} in {year}: {error_msg}"
                    )
                    logging.error(
                        f"Error processing country {code} trading with {code2} in {year}: {error_msg}"
                    )
                continue
