import json
import os
import time
from pprint import pprint

import pandas as pd
import requests


def save_checkpoint(
    page_number, total_records, checkpoint_file="scraper_checkpoint.json"
):
    """Save the current scraping progress to a checkpoint file."""
    checkpoint_data = {
        "last_completed_page": page_number,
        "total_records_collected": total_records,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint_data, f, indent=4)
    print(f"Checkpoint saved: Page {page_number}, {total_records} records")


def load_checkpoint(checkpoint_file="scraper_checkpoint.json"):
    """Load the most recent checkpoint if it exists."""
    if not os.path.exists(checkpoint_file):
        return None, 0
    try:
        with open(checkpoint_file, "r") as f:
            data = json.load(f)
        print(f"Found checkpoint from {data.get('timestamp', 'unknown time')}")
        print(f"Resuming from page {data.get('last_completed_page', 0) + 1}")
        return data.get("last_completed_page"), data.get("total_records_collected", 0)
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        return None, 0


def call_unctad_api(page_number=1, max_retries=3, retry_delay=5):
    """Make a POST request to the UNCTAD TRAINS API with retry logic."""
    url = "https://api-trains2.unctad.org/denormalisedMeasures"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://trainsonline.unctad.org",
        "Referer": "https://trainsonline.unctad.org/",
    }

    try:
        with open("NTM_payload.json") as f:
            payload = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading payload: {e}")
        return None

    payload["pageNumber"] = page_number
    session = requests.Session()

    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                wait_time = retry_delay * (2 ** (attempt - 1))
                print(f"Retry {attempt}/{max_retries}, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)

            response = session.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", retry_delay))
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            if attempt >= max_retries:
                if response.text:
                    try:
                        print("Error details:", response.json())
                    except:
                        print("Response:", response.text[:500])
                return None


def process_page_data(data, output_file=None, append=False, all_columns=None):
    """Process the API response for a single page."""
    if not data:
        return None, None

    if all_columns is None:
        all_columns = [
            "measureId",
            "imposingCountriesId",
            "countryImposingNTMs",
            "ntmCode",
            "ntmDescription",
            "measureDescription",
            "productDescription",
            "hsCode",
            "issuingAgency",
            "regulationTitle",
            "regulationSymbol",
            "implementationDate",
            "affectedCountriesNames",
            "productIds",
            "ntmType",
            "isUnilateral",
            "repealDate",
            "isHorizontalMeasure",
            "regulationFile",
            "regulationOfficialTitleOriginal",
            "measureDescriptionOriginal",
            "measureProductDescriptionOriginal",
            "supportingRegulations",
            "measureObjectivesOriginal",
            "yearsOfDataCollection",
            "selectedHSCodes",
            "countriesWhichMatchSelection",
            "countriesWhichDoesNotMatchSelection",
            "objectiveCodes",
        ]

    if isinstance(data, dict):
        for field in ["content", "data", "results", "items", "measures"]:
            if field in data and isinstance(data[field], list):
                data_list = data[field]
                break
        else:
            return None, None
    else:
        data_list = data

    try:
        df = pd.DataFrame(data_list)
        for col in all_columns:
            if col not in df.columns:
                df[col] = pd.NA
        df = df.reindex(columns=[col for col in all_columns if col in df.columns])

        if output_file:
            mode = "a" if append and os.path.exists(output_file) else "w"
            df.to_csv(output_file, mode=mode, header=(mode == "w"), index=False)
            print(f"{'Appended' if mode == 'a' else 'Created'} {len(df)} records")

        return df, {"total_records": len(df), "columns": list(df.columns)}
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None


def scrape_all_pages(
    start_page=1,
    end_page=1590,
    output_file="unctad_ntm_data.csv",
    checkpoint_interval=5,
    checkpoint_file="scraper_checkpoint.json",
):
    """Scrape all pages from the UNCTAD API and combine results."""
    last_page, all_records = load_checkpoint(checkpoint_file)
    if last_page is not None:
        start_page = last_page + 1
        start_new_file = False
    else:
        all_records = 0
        start_new_file = True

    if start_new_file and os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed existing {output_file}")

    try:
        for page in range(start_page, end_page + 1):
            print(f"\nProcessing page {page}/{end_page}")
            data = call_unctad_api(page_number=page)

            if data:
                _, stats = process_page_data(
                    data,
                    output_file=output_file,
                    append=(page > start_page or not start_new_file),
                )

                if stats:
                    all_records += stats["total_records"]
                    print(f"Progress: {all_records} records")

                    if page % checkpoint_interval == 0 or page == end_page:
                        save_checkpoint(page, all_records, checkpoint_file)

                if page < end_page:
                    time.sleep(0.5)
            else:
                print(f"Failed page {page}")
                save_checkpoint(page - 1, all_records, checkpoint_file)

    except KeyboardInterrupt:
        print("\nScraping interrupted")
        save_checkpoint(page - 1, all_records, checkpoint_file)
        return all_records
    except Exception as e:
        print(f"\nError: {e}")
        save_checkpoint(page - 1, all_records, checkpoint_file)
        return all_records

    print(f"\nCompleted. Total records: {all_records}")
    save_checkpoint(end_page, all_records, checkpoint_file)
    return all_records


def main():
    """Main entry point for the scraper."""
    print("Starting UNCTAD TRAINS API scraper")
    last_page, records = load_checkpoint()

    if last_page is not None:
        resume = input(f"Resume from page {last_page + 1}? (y/n): ").lower()
        if resume != "y":
            confirm = input(
                "Start from beginning? This will overwrite existing data. (y/n): "
            ).lower()
            if confirm != "y":
                print("Exiting")
                return
            os.remove("scraper_checkpoint.json")
            print("Starting from page 1...")

    total_records = scrape_all_pages()
    if total_records > 0:
        print(f"Data collection complete. Results saved to unctad_ntm_data.csv")
    else:
        print("Failed to collect data")


if __name__ == "__main__":
    main()
