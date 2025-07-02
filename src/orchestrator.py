import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime
import pydantic
from dotenv import load_dotenv

from .components.pdf_processor import PDFProcessor
from .components.llm_clients import LLMClientFactory
from .models.schemas import (
    ExtractedFile, 
    OfferTemplate, 
    FinalResult, 
    LLMRequest
)

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    def __init__(self, config=None):
        """Initialize the workflow orchestrator"""
        self.config = config or {}
        self.pdf_processor = PDFProcessor()
        load_dotenv()  # Load environment variables
        
    def run(self, input_folder: str, output_folder: str, extraction_method: str, llm_provider: str):
        """Main application logic as described in PRD Section 3"""
        logger.info(f"Starting workflow: input={input_folder}, output={output_folder}, method={extraction_method}, llm={llm_provider}")
        
        try:
            # F-01: List all PDF files in input folder
            input_path = Path(input_folder)
            if not input_path.exists():
                raise FileNotFoundError(f"Input folder not found: {input_folder}")
            
            pdf_files = list(input_path.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in {input_folder}")
                return
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # F-02 & F-03: Extract text from each PDF
            extracted_files = []
            for pdf_file in pdf_files:
                logger.info(f"Processing {pdf_file.name}...")
                extracted_file = self.pdf_processor.extract(str(pdf_file), extraction_method)
                extracted_files.append(extracted_file)
                
                # F-04: Save intermediate JSON for each file
                self._save_extracted_file(extracted_file, output_folder)
            
            # F-05: Aggregate all extracted text
            consolidated_text = self._consolidate_text(extracted_files)
            
            # F-06: Construct LLM prompt
            prompt = self._construct_prompt(consolidated_text)
            
            # F-07: Call LLM
            llm_client = LLMClientFactory.create_client(llm_provider)
            source_filenames = [ef.filename for ef in extracted_files]
            
            logger.info(f"Sending consolidated text to {llm_provider} LLM...")
            llm_response = llm_client.get_structured_offer(prompt)
            
            # F-08: Parse and validate response
            offer_template = OfferTemplate.model_validate(llm_response)
            
            # F-09: Create final result
            final_result = FinalResult(
                request_details=LLMRequest(
                    prompt_sent=prompt,
                    llm_provider=llm_provider,
                    llm_model=self._get_model_name(llm_provider),
                    source_filenames=source_filenames
                ),
                filled_offer=offer_template,
                llm_response_raw=llm_response,
                processing_timestamp=datetime.now()
            )
            
            # F-10: Save final result
            self._save_final_result(final_result, output_folder)
            
            logger.info("Workflow completed successfully")
            
        except FileNotFoundError as e:
            logger.error(f"File/folder not found: {str(e)}")
            raise
        except pydantic.ValidationError as e:
            logger.error(f"LLM response validation failed: {str(e)}")
            # Save failed response for debugging
            self._save_failed_response(llm_response if 'llm_response' in locals() else None, output_folder)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _save_extracted_file(self, extracted_file: ExtractedFile, output_folder: str):
        """F-04: Save intermediate extracted data"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{Path(extracted_file.filename).stem}_extracted.json"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_file.model_dump(), f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Saved extracted data to {file_path}")
    
    def _consolidate_text(self, extracted_files: List[ExtractedFile]) -> str:
        """F-05: Consolidate all extracted text as per PRD pseudocode"""
        page_separator = "\n\n--- PAGE BREAK ---\n\n"
        file_separator = "\n\n--- NEW FILE: {filename} ---\n\n"
        consolidated_text = ""
        
        for extracted_file in extracted_files:
            consolidated_text += file_separator.format(filename=extracted_file.filename)
            page_contents = [page.content for page in extracted_file.pages]
            consolidated_text += page_separator.join(page_contents)
        
        return consolidated_text
    
    def _construct_prompt(self, consolidated_text: str) -> str:
        """F-06: Construct the final prompt"""
        # Load prompt template
        prompt_template_path = Path(__file__).parent.parent / "config" / "prompt_template.md"
        with open(prompt_template_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        # Get the OfferTemplate schema as string with Polish comments
        # We'll extract this from the source code to preserve comments
        schemas_path = Path(__file__).parent / "models" / "schemas.py"
        with open(schemas_path, 'r', encoding='utf-8') as f:
            schemas_content = f.read()
        
        # Extract just the OfferTemplate and related classes with comments
        # This is a simplified approach - in production you might want a more robust parser
        schema_section = self._extract_schema_section(schemas_content)
        
        # Construct final prompt
        prompt = f"{prompt_template}\n\n"
        prompt += "JSON Schema (as Pydantic Model):\n```python\n"
        prompt += schema_section
        prompt += "\n```\n\n"
        prompt += f"OCR Text:\n{consolidated_text}"
        
        return prompt
    
    def _extract_schema_section(self, schemas_content: str) -> str:
        """Extract relevant schema classes with Polish comments"""
        # Find the start of target models
        start_marker = "# --- Target Offer Template Models"
        end_marker = "# --- Final Result Model"
        
        start_idx = schemas_content.find(start_marker)
        end_idx = schemas_content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            # Fallback: include everything from FormInfo to OfferTemplate
            return schemas_content
        
        # Extract the relevant section
        relevant_section = schemas_content[start_idx:end_idx].strip()
        
        # Also need to include imports
        imports = """from pydantic import BaseModel, Field
from typing import List"""
        
        return f"{imports}\n\n{relevant_section}"
    
    def _get_model_name(self, llm_provider: str) -> str:
        """Get the model name for the LLM provider"""
        model_map = {
            "openai": "gpt-4-turbo",
            "claude": "claude-3-opus-20240229",
            "gemini": "gemini-pro"
        }
        return model_map.get(llm_provider, "unknown")
    
    def _save_final_result(self, final_result: FinalResult, output_folder: str):
        """F-10: Save the final result"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"filled_offer_{timestamp}.json"
        file_path = output_path / filename
        
        # Save just the filled offer as per PRD
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(final_result.filled_offer.model_dump(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved filled offer to {file_path}")
        
        # Also save complete result for debugging (optional)
        debug_filename = f"complete_result_{timestamp}.json"
        debug_path = output_path / debug_filename
        with open(debug_path, 'w', encoding='utf-8') as f:
            # Convert datetime to string for JSON serialization
            result_dict = final_result.model_dump()
            result_dict['processing_timestamp'] = final_result.processing_timestamp.isoformat()
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Saved complete result to {debug_path}")
    
    def _save_failed_response(self, response: any, output_folder: str):
        """Save failed LLM response for debugging"""
        if response is None:
            return
        
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"failed_response_{timestamp}.json"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(response, dict):
                json.dump(response, f, ensure_ascii=False, indent=2)
            else:
                json.dump({"raw_response": str(response)}, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved failed response to {file_path}")