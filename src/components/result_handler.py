import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

from ..models.schemas import FinalResult, OfferTemplate

logger = logging.getLogger(__name__)


class ResultHandler:
    """Handles validation and saving of results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_offer(self, offer_data: dict) -> OfferTemplate:
        """Validate offer data against the OfferTemplate schema"""
        try:
            return OfferTemplate.model_validate(offer_data)
        except Exception as e:
            self.logger.error(f"Offer validation failed: {str(e)}")
            raise
    
    def save_offer(self, offer: OfferTemplate, output_folder: str, filename_prefix: str = "filled_offer") -> Path:
        """Save the filled offer to JSON file"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(offer.model_dump(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved offer to {file_path}")
        return file_path
    
    def save_complete_result(self, result: FinalResult, output_folder: str) -> Path:
        """Save the complete result including metadata"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_result_{timestamp}.json"
        file_path = output_path / filename
        
        # Convert datetime to string for JSON serialization
        result_dict = result.model_dump()
        result_dict['processing_timestamp'] = result.processing_timestamp.isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        self.logger.debug(f"Saved complete result to {file_path}")
        return file_path
    
    def save_failed_response(self, response: Any, output_folder: str, error: Optional[Exception] = None) -> Path:
        """Save failed LLM response for debugging"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"failed_response_{timestamp}.json"
        file_path = output_path / filename
        
        error_data = {
            "timestamp": timestamp,
            "error": str(error) if error else "Unknown error",
            "response": response if isinstance(response, dict) else str(response)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved failed response to {file_path}")
        return file_path
    
    def save_extracted_files(self, extracted_files: list, output_folder: str):
        """Save intermediate extracted files"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for extracted_file in extracted_files:
            filename = f"{Path(extracted_file.filename).stem}_extracted.json"
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_file.model_dump(), f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Saved extracted data to {file_path}")
    
    def load_offer_from_file(self, file_path: str) -> OfferTemplate:
        """Load and validate an offer from a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self.validate_offer(data)
    
    def compare_offers(self, offer1: OfferTemplate, offer2: OfferTemplate) -> dict:
        """Compare two offers and return differences"""
        dict1 = offer1.model_dump()
        dict2 = offer2.model_dump()
        
        differences = {}
        self._compare_dicts(dict1, dict2, differences)
        
        return differences
    
    def _compare_dicts(self, d1: dict, d2: dict, differences: dict, path: str = ""):
        """Recursively compare two dictionaries"""
        all_keys = set(d1.keys()) | set(d2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key not in d1:
                differences[current_path] = {"status": "added", "value": d2[key]}
            elif key not in d2:
                differences[current_path] = {"status": "removed", "value": d1[key]}
            elif d1[key] != d2[key]:
                if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    self._compare_dicts(d1[key], d2[key], differences, current_path)
                else:
                    differences[current_path] = {
                        "status": "changed",
                        "old_value": d1[key],
                        "new_value": d2[key]
                    }