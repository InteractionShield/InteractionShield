#!/usr/bin/env python3
from pathlib import Path
from openpyxl import Workbook

APPS_DIR = Path("/InteractionShield/artifact/Intermediate/apps")
OUTPUT_XLSX = Path("/InteractionShield/artifact/Intermediate/config/ConfigInfo.xlsx")

def main():
    if not APPS_DIR.exists():
        raise FileNotFoundError(f"Folder not found: {APPS_DIR}")

    files = sorted([p for p in APPS_DIR.iterdir() if p.is_file()])
    if not files:
        raise FileNotFoundError(f"No files found in {APPS_DIR}")

    wb = Workbook()
    # Remove the default sheet
    default = wb.active
    wb.remove(default)

    for f in files:
        name = f.stem

        ws = wb.create_sheet(title=name)
        ws.append(["randTrigger", name+"Trigger"])
        ws.append(["randAction", name+"Action"])

    wb.save(OUTPUT_XLSX)
    print(f"Done. Wrote {len(files)} sheets to {OUTPUT_XLSX}")

if __name__ == "__main__":
    main()
