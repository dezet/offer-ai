#!/usr/bin/env python3
import logging
import sys
from pathlib import Path
import typer
from typing import Optional
from dotenv import load_dotenv

from .orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="offer-filler",
    help="Automated Offer Form Filler - Extract data from PDFs and fill offer templates using LLMs"
)


@app.command()
def process(
    input_folder: str = typer.Option(
        ...,
        "--input-folder", "-i",
        help="Path to folder containing PDF files to process"
    ),
    output_folder: str = typer.Option(
        ...,
        "--output-folder", "-o",
        help="Path to folder where results will be saved"
    ),
    extraction_method: str = typer.Option(
        "text",
        "--extraction-method", "-m",
        help="PDF text extraction method: 'ocr' or 'text'"
    ),
    llm_provider: str = typer.Option(
        "openai",
        "--llm-provider", "-p",
        help="LLM provider to use: 'openai', 'claude', or 'gemini'"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose logging"
    )
):
    """
    Process PDF files and fill the offer template using LLM.
    
    This command will:
    1. Read all PDF files from the input folder
    2. Extract text using the specified method (OCR or text layer)
    3. Send the consolidated text to the selected LLM
    4. Parse and validate the response
    5. Save the filled offer template to the output folder
    """
    
    # Set logging level based on verbose flag
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate inputs
    if extraction_method not in ["ocr", "text"]:
        typer.echo(f"Error: Invalid extraction method '{extraction_method}'. Use 'ocr' or 'text'.", err=True)
        raise typer.Exit(1)
    
    if llm_provider not in ["openai", "claude", "gemini"]:
        typer.echo(f"Error: Invalid LLM provider '{llm_provider}'. Use 'openai', 'claude', or 'gemini'.", err=True)
        raise typer.Exit(1)
    
    # Check if input folder exists
    if not Path(input_folder).exists():
        typer.echo(f"Error: Input folder not found: {input_folder}", err=True)
        raise typer.Exit(1)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Create and run orchestrator
        typer.echo(f"Starting processing...")
        typer.echo(f"Input folder: {input_folder}")
        typer.echo(f"Output folder: {output_folder}")
        typer.echo(f"Extraction method: {extraction_method}")
        typer.echo(f"LLM provider: {llm_provider}")
        
        orchestrator = WorkflowOrchestrator()
        orchestrator.run(
            input_folder=input_folder,
            output_folder=output_folder,
            extraction_method=extraction_method,
            llm_provider=llm_provider
        )
        
        typer.echo(" Processing completed successfully!")
        typer.echo(f"Results saved to: {output_folder}")
        
    except FileNotFoundError as e:
        typer.echo(f"L Error: {str(e)}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"L Configuration error: {str(e)}", err=True)
        typer.echo("Make sure you have set the required API keys in your .env file or environment variables.", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"L Unexpected error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def validate(
    offer_file: str = typer.Argument(
        ...,
        help="Path to JSON file containing offer data to validate"
    )
):
    """
    Validate an offer JSON file against the schema.
    """
    from .components.result_handler import ResultHandler
    
    try:
        handler = ResultHandler()
        offer = handler.load_offer_from_file(offer_file)
        typer.echo(f" Valid offer file: {offer_file}")
        typer.echo(f"Project: {offer.formInfo.projectContract}")
        typer.echo(f"Investor: {offer.formInfo.investor}")
        typer.echo(f"Version: {offer.formInfo.version}")
    except Exception as e:
        typer.echo(f"L Invalid offer file: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def compare(
    file1: str = typer.Argument(..., help="First offer file to compare"),
    file2: str = typer.Argument(..., help="Second offer file to compare")
):
    """
    Compare two offer JSON files and show differences.
    """
    from .components.result_handler import ResultHandler
    
    try:
        handler = ResultHandler()
        offer1 = handler.load_offer_from_file(file1)
        offer2 = handler.load_offer_from_file(file2)
        
        differences = handler.compare_offers(offer1, offer2)
        
        if not differences:
            typer.echo(" The offers are identical.")
        else:
            typer.echo(f"Found {len(differences)} differences:")
            for path, diff in differences.items():
                if diff["status"] == "changed":
                    typer.echo(f"  - {path}: '{diff['old_value']}' ’ '{diff['new_value']}'")
                elif diff["status"] == "added":
                    typer.echo(f"  + {path}: '{diff['value']}'")
                elif diff["status"] == "removed":
                    typer.echo(f"  - {path}: '{diff['value']}'")
    except Exception as e:
        typer.echo(f"L Error comparing files: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """
    Show version information.
    """
    typer.echo("Automated Offer Form Filler v1.0.0")
    typer.echo("Copyright (c) 2023")


def main():
    """Main entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()