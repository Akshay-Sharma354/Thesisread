import os
import glob
import json

from config import SAMPLE_DATA_DIR
from models import FilingInput
from pipeline import run_pipeline

FILE_TO_COMPANY = {
    "01_infratech_results.txt": ("Infratech Solutions Limited", "INFRATECH"),
    "02_greenharvest_rpt1.txt": ("GreenHarvest Agro Limited", "GRNHARV"),
    "03_greenharvest_rpt2.txt": ("GreenHarvest Agro Limited", "GRNHARV"),
    "04_northstar_auditor_resignation.txt": ("Northstar Pharmaceuticals Limited", "NORTHSTARPH"),
    "05_coastal_compliance_cert.txt": ("Coastal Logistics Limited", "COASTALLOG"),
}

def main():
    files = sorted(glob.glob(os.path.join(SAMPLE_DATA_DIR, "*.txt")))
    for path in files:
        fname = os.path.basename(path)
        if fname not in FILE_TO_COMPANY:
            print(f"Skipping {fname} - no company mapping defined")
            continue

        company_name, ticker = FILE_TO_COMPANY[fname]
        with open(path, "r") as f:
            raw_text = f.read()

        print(f"\n--- Analyzing {fname} ({company_name}) ---")
        filing = FilingInput(company_name=company_name, ticker=ticker, raw_text=raw_text)
        analysis = run_pipeline(filing)

        print(f"Headline: {analysis['alert_headline']}")
        print(f"Significance: {analysis['significance']['significance_score']}/10 ({analysis['significance']['sentiment']})")
        if analysis['comparison']['pattern_note']:
            print(f"Pattern: {analysis['comparison']['pattern_note']}")

    print("\nDone. Start the API with `uvicorn main:app --reload` and open the frontend.")

if __name__ == "__main__":
    main()
