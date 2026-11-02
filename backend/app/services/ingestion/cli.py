"""
Command Line Interface for WindScope India Data Ingestion Pipeline.
Usage:
    python backend/app/services/ingestion/cli.py ingest-cea --file <path> --year <YYYY> --month <M>
"""

import sys
import argparse
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.core.database import SessionLocal
from app.services.ingestion.pipeline import run_cea_ingestion_pipeline, IngestionPipelineError


def main():
    parser = argparse.ArgumentParser(description="WindScope India Data Ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingest CEA command
    cea_parser = subparsers.add_parser("ingest-cea", help="Ingest a CEA monthly renewable generation file")
    cea_parser.add_argument("--file", required=True, type=str, help="Path to raw CSV or XLSX file")
    cea_parser.add_argument("--year", required=True, type=int, help="Reporting year (e.g. 2024)")
    cea_parser.add_argument("--month", required=True, type=int, help="Reporting month (1-12)")
    cea_parser.add_argument("--source-org", default="Central Electricity Authority (RPM Division)", help="Publishing organization")
    cea_parser.add_argument("--dataset-name", default="Broad Overview of Monthly Renewable Energy Generation", help="Dataset title")
    cea_parser.add_argument("--url", default="https://cea.nic.in/renewable-generation-report/?lang=en", help="Source URL")
    cea_parser.add_argument("--allow-reprocessing", action="store_true", help="Allow re-ingesting already hashed files")

    args = parser.parse_args()

    if args.command == "ingest-cea":
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File does not exist: {file_path}")
            sys.exit(1)

        db = SessionLocal()
        try:
            print(f"Starting ingestion of {file_path.name} for {args.year}-{args.month:02d}...")
            result = run_cea_ingestion_pipeline(
                db=db,
                file_path=file_path,
                reporting_year=args.year,
                reporting_month=args.month,
                source_org=args.source_org,
                dataset_name=args.dataset_name,
                source_url=args.url,
                allow_reprocessing=args.allow_reprocessing,
            )
            print("==================================================")
            print("INGESTION SUCCESSFUL")
            print(f"Source File ID: {result['source_file_id']}")
            print(f"Archived Name : {result['filename']}")
            print(f"Period        : {result['reporting_period']}")
            print(f"Records Extr. : {result['records_processed']}")
            print(f"Inserted      : {result['records_inserted']}")
            print(f"Updated       : {result['records_updated']}")
            print(f"Duration      : {result['execution_time_seconds']}s")
            print("Reconciliation Summary:")
            for fuel, recon in result["reconciliations"].items():
                print(f"  - {fuel:12}: States={recon['sum_of_states_mu']:10.2f} MU | Reported={recon.get('reported_national_total_mu', 'N/A')} MU | Status={recon['validation_status']}")
            print("==================================================")
        except IngestionPipelineError as e:
            print(f"Ingestion Failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            sys.exit(1)
        finally:
            db.close()


if __name__ == "__main__":
    main()
