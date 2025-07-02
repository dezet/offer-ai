Of course. Here is the complete, final PRD, rewritten and optimized to be used as a direct input for an AI code generation agent. It is highly prescriptive, providing exact file structures, class signatures, and implementation details to minimize ambiguity and guide the agent toward the desired output.

---

## **Product Requirements Document: Automated Offer Form Filler**

| **Document Version** | 1.2 |
| :--- | :--- |
| **Date** | 2023-10-27 |
| **Status** | **Final for AI Agent** |
| **Purpose** | This document provides a detailed, machine-actionable implementation plan for an AI agent to generate the application code. |

### 1. Introduction & Vision

**1.1. Overview**
This document outlines the requirements for the "Automated Offer Form Filler," a command-line application designed to streamline the process of populating a standardized offer template. The system will read a collection of PDF documents, extract their textual content using Optical Character Recognition (OCR) or by reading the text layer, and leverage a Large Language Model (LLM) to intelligently find and place the relevant information into a target JSON structure.
You can find offer template in offer_template.json file.
**1.2. Project Goal**
The primary goal is to automate the data extraction and population of the offer form, significantly reducing manual effort, minimizing errors, and accelerating the offer preparation lifecycle. This tool will act as a "data extraction expert," providing a structured, machine-readable output from unstructured documents.

### 2. User Personas

*   **Bidding Engineer (Primary User):** Responsible for preparing technical and commercial offers. Needs a fast, reliable way to consolidate data from project files into a standard format.
*   **Developer/Data Scientist (System Maintainer):** Responsible for building, maintaining, and extending the tool.

### 3. Functional Requirements & Implementation Logic

This section details the step-by-step logic the application must follow.

| ID | Requirement | Implementation Instruction |
| :--- | :--- | :--- |
| **F-01** | **Local Folder Input** | The application must accept a path to a local directory via a `--input-folder` command-line argument. Use Python's `os` or `pathlib` module to list all files ending with `.pdf` in this directory. |
| **F-02** | **PDF Text Extraction** | Based on the `--extraction-method` argument (`ocr` or `text`), select the appropriate extraction strategy for each PDF file. |
| **F-03** | **Intermediate Data Structuring** | For each processed PDF, populate an `ExtractedFile` Pydantic model (defined in Section 6) with the filename, extraction method, and a list of `ExtractedPage` models containing the content. |
| **F-04** | **Intermediate Output Generation** | After processing each PDF, serialize its `ExtractedFile` model to a JSON string and save it to the directory specified by `--output-folder`. The filename shall be `[original_filename]_extracted.json`. |
| **F-05** | **LLM Data Aggregation** | Create a single string variable named `consolidated_text`. Iterate through the list of `ExtractedFile` objects. For each file, prepend a file header and join the content of its pages with a page separator. <br>**Pseudocode:**<br>```python<br>page_separator = "\n\n--- PAGE BREAK ---\n\n"<br>file_separator = "\n\n--- NEW FILE: {filename} ---\n\n"<br>consolidated_text = ""<br>for extracted_file in list_of_extracted_files:<br>    consolidated_text += file_separator.format(filename=extracted_file.filename)<br>    page_contents = [page.content for page in extracted_file.pages]<br>    consolidated_text += page_separator.join(page_contents)<br>``` |
| **F-06** | **LLM Prompting** | Construct the final prompt string by concatenating: <br> 1. The content of the `config/prompt_template.md` file. <br> 2. The empty `OfferTemplate` JSON schema (as a string). <br> 3. The `consolidated_text` from F-05. |
| **F-07** | **LLM Integration** | Use a factory pattern to select the LLM client based on the `--llm-provider` argument (`openai`, `claude`, or `gemini`). Call the client with the constructed prompt. |
| **F-08** | **LLM Response Parsing** | The LLM will return a JSON string. Parse this string into a Python dictionary. Then, use Pydantic's `OfferTemplate.model_validate()` method to validate and load the dictionary into the Pydantic model. |
| **F-09** | **Final Result Structuring** | Instantiate the `FinalResult` Pydantic model. Populate its fields (`request_details`, `filled_offer`, etc.) with the data from the current session. |
| **F-10** | **Final Output Persistence** | Serialize the `filled_offer` attribute of the `FinalResult` model to a JSON string. Save it to the `--output-folder` with the filename `filled_offer_[timestamp].json`. |

### 4. System Architecture & Implementation Plan

#### **4.1. Directory and File Structure**
Create the project with the following exact directory structure:
```
/automated-offer-filler/
│
├── src/
│   ├── __init__.py
│   ├── main.py                # CLI Entrypoint using Typer/Argparse
│   ├── orchestrator.py        # WorkflowOrchestrator class
│   ├── components/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py   # Extraction strategies
│   │   ├── llm_clients.py     # All LLM client implementations
│   │   └── result_handler.py  # Result validation and saving logic
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # All Pydantic models
│
├── config/
│   └── prompt_template.md     # The LLM prompt instructions
│
├── requirements.txt
└── .env
```

#### **4.2. Component Interfaces (Function Signatures)**
Implement the classes and methods with these exact signatures in the specified files.

**File: `src/models/schemas.py`**
*   This file will contain all Pydantic models as defined in **Section 6** of this document.

**File: `src/components/pdf_processor.py`**
```python
from abc import ABC, abstractmethod
from ..models.schemas import ExtractedFile

class BaseExtractionStrategy(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> ExtractedFile:
        raise NotImplementedError

class OCRExtractionStrategy(BaseExtractionStrategy):
    def extract(self, file_path: str) -> ExtractedFile:
        # Implementation using pytesseract and Pillow
        pass

class TextLayerExtractionStrategy(BaseExtractionStrategy):
    def extract(self, file_path: str) -> ExtractedFile:
        # Implementation using PyMuPDF (fitz)
        pass
```

**File: `src/components/llm_clients.py`**
```python
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def get_structured_offer(self, prompt: str) -> dict:
        raise NotImplementedError

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        # init client
        pass
    def get_structured_offer(self, prompt: str) -> dict:
        # implement API call to OpenAI
        pass

# Also implement ClaudeClient and GeminiClient, inheriting from BaseLLMClient
```

**File: `src/orchestrator.py`**
```python
class WorkflowOrchestrator:
    def __init__(self, config):
        # store config if needed
        pass
    def run(self, input_folder: str, output_folder: str, extraction_method: str, llm_provider: str):
        # Implement the main application logic here as described in Section 3
        pass
```

### 5. Non-Functional Requirements

| ID | Requirement | Implementation Instruction |
| :--- | :--- | :--- |
| **NF-01** | **Configuration** | Use the `python-dotenv` library to load environment variables from a `.env` file. The required variables are `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GOOGLE_API_KEY`. |
| **NF-02** | **Logging** | Use Python's built-in `logging` module. Configure a basic logger that prints messages to the console with the format: `[TIMESTAMP] [LEVEL] - MESSAGE`. |
| **NF-03** | **Error Handling** | In `WorkflowOrchestrator.run`, wrap the main logic in a `try...except` block. <br>- `except FileNotFoundError`: Log an error "Input/Output folder not found" and exit. <br>- `except pydantic.ValidationError as e`: Log the validation error and save the raw, invalid LLM response to a file named `failed_response_[timestamp].json` for debugging. <br>- `except Exception as e`: Log any other unexpected error. |
| **NF-04** | **Dependencies** | The project dependencies are defined in `requirements.txt`. Create this file with the exact content specified in **Section 7.1**. |

### 6. Data Models (Pydantic Schemas)

**Instruction:** Create the file `src/models/schemas.py` with the following **exact and complete** content.

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime

# --- Intermediate Extraction Models ---

class ExtractedPage(BaseModel):
    page_number: int
    content: str

class ExtractedFile(BaseModel):
    filename: str
    extraction_method: Literal['ocr', 'text']
    pages: List[ExtractedPage]

# --- Target Offer Template Models ---

class FormInfo(BaseModel):
    description: str
    documentTitle: str
    documentVersion: str
    projectCaretakersDPI: str
    projectCaretakersRealization: str
    updateDates: List[str]
    version: int
    projectContract: str
    investor: str
    offerMode: str
    requiredCompletionDate: str

class GeneralData(BaseModel):
    description: str
    connectionPower: str
    maxPowerNcRfg: str
    activePowerLimitPcc: str
    connectionVoltage: str
    shortCircuitCurrentPcc: str
    otherImportantInfo: str

class Connection(BaseModel):
    description: str
    connectionLength: str
    cableSlackGuideline: str
    shortCircuitStrengthRequirements: str
    conductorMaterial: str
    allowConductorGrading: str
    allowReturnConductorGrading: str
    otherSpecialRequirements: str
    allowedDailyLoadFactor: str
    maxLayingDepth: str
    concreteBentoniteRequirement: str
    otherObjectsLimitingLoad: str
    otherConnectionNotes: str

class Gpo(BaseModel):
    description: str
    stationLayoutAndConditions: str
    compensationType: str
    structureSolutions: str
    switchgearType: str
    otherGpoNotes: str

class PowerTransformer(BaseModel):
    description: str
    minPower: str
    requiredShortCircuitVoltage: str
    requiredHvMvRatio: str
    minTapChangerRange: str
    tapChangerType: str
    insulationLevelHvMv: str
    maxNoLoadLoadLosses: str
    coolingType: str
    bushingType: str
    noLoadCurrent: str
    otherTransformerNotes: str

class MvSwitchgear(BaseModel):
    description: str
    operatingMaxVoltage: str
    shortCircuitStrengthAndTime: str
    peakWithstandCurrent: str
    busbarContinuousCurrent: str
    requiredBayTypesAndCount: str
    requiredInsulationLevel: str
    recommendedSolutions: str
    otherSwitchgearNotes: str

class MvTopology(BaseModel):
    description: str
    minConductorCrossSection: str
    maxConductorCrossSection: str
    allowedDailyLoadFactorMv: str
    specialShortCircuitRequirements: str
    conductorMaterialMv: str
    minCableLayingDepth: str
    cableSlackGuidelineMv: str
    maxVoltageDropPowerLoss: str
    neutralPointGroundingMethod: str
    returnConductorShortCircuitStrength: str
    otherTopologyNotes: str

class PvGeneration(BaseModel):
    description: str
    inverterTypeAndCount: str
    panelTypeAndCount: str
    deviationsFromConditions: str
    pvStationTypeCountAndPower: str
    topologyDrawingFile: str
    allowNighttimeReactivePower: str
    allowReactivePowerRegulation: str
    pvsystSimulationParameters: str
    constructionType: str
    preferredTableDimensions: str
    otherRequirements: str
    projectLayoutMapFile: str
    preferredPanelWiring: str
    permissibleInstallationParametersDS: str
    permissibleInstallationParametersWZ: str
    preferredDcAcRatio: str
    otherPvGenerationNotes: str

class WindGeneration(BaseModel):
    description: str
    turbineTypeAndCount: str
    fwTopologyDrawingFile: str
    turbineReactivePowerCapability: str
    reactivePowerLimitations: str
    activePowerCurtailment: str
    turbineTransformerData: str
    maxMvCrossSectionToTurbine: str
    otherWindGenerationNotes: str

class OtherAtypicalRequirements(BaseModel):
    description: str
    preferredManufacturers: str
    otherNotes: str

class InternalMvCable(BaseModel):
    from_loc: str = Field(..., alias='from')
    to: str
    routeLengthKm: float
    inverterCount: int
    powerMva: float
    currentA: float
    conductorCrossSectionMm2: int
    returnCrossSectionMm2: int
    coresPerPhase: int

class RequiredScope(BaseModel):
    description: str
    tableLengthRequest: str
    mvLvStationQuantityCheck: str
    inverterQuantityCheck: str
    internalMvLineCheck: str
    internalMvCableNotes: str
    internalMvCables: List[InternalMvCable]
    dcCableQuantityAndCrossSectionRequest: str
    acCableQuantityAndCrossSectionRequest: str
    cableJointsConceptCheck: str
    powerEvacuationMvLineCheck: str
    newConceptRequest: str
    tableAndStringLengthForNewPanelsRequest: str
    dcCableQuantityAndCrossSectionRequestNew: str
    acCableQuantityAndCrossSectionRequestNew: str
    mvLvStationQuantityCheckNew: str
    inverterQuantityCheckNew: str
    reactivePowerRegulationNote: str

class Selections(BaseModel):
    description: str
    selectionA: str
    selectionB: str

class OfferTemplate(BaseModel):
    formInfo: FormInfo
    generalData: GeneralData
    connection: Connection
    gpo: Gpo
    powerTransformer: PowerTransformer
    mvSwitchgear: MvSwitchgear
    mvTopology: MvTopology
    pvGeneration: PvGeneration
    windGeneration: WindGeneration
    otherAtypicalRequirements: OtherAtypicalRequirements
    requiredScope: RequiredScope
    selections: Selections

# --- Final Result Model ---

class LLMRequest(BaseModel):
    prompt_sent: str
    llm_provider: str
    llm_model: str
    source_filenames: List[str]

class FinalResult(BaseModel):
    request_details: LLMRequest
    filled_offer: OfferTemplate
    llm_response_raw: Union[dict, str]
    processing_timestamp: datetime
```

### 7. Configuration and Dependency Files

#### 7.1. `requirements.txt`
Create a file named `requirements.txt` with the following exact content:
```
pydantic~=2.5
openai~=1.3
anthropic~=0.7
google-generativeai~=0.3
python-dotenv~=1.0
PyMuPDF~=1.23
pytesseract~=0.3
Pillow~=10.1
typer~=0.9
```

#### 7.2. `config/prompt_template.md`
Create a file named `prompt_template.md` inside the `config` directory with the following exact content:
```markdown
Objective:
Your task is to act as an expert data extraction engine. You will receive an empty JSON template and a block of text extracted from a document via OCR. Your goal is to accurately populate the JSON template with the corresponding information found in the OCR text.

Inputs:
JSON Template (JSON_TEMPLATE): A predefined JSON structure with empty fields. Each field has a descriptive English key.
OCR Text (OCR_TEXT): The raw text content extracted from one or more source documents.

Instructions:
1.  **Field Matching:** For each field in the JSON_TEMPLATE, use its English key to locate the corresponding information in the OCR_TEXT. The text may contain Polish labels which correspond to these keys.
2.  **Value Extraction:**
    *   Carefully extract the value associated with each label. The value may be on the same line, on the line below, or in a related paragraph.
    *   For long text fields like `otherRequirements` or `powerEvacuationMvLineCheck`, extract the entire relevant paragraph or multi-line text.
    *   For simple fields like `version` or `constructionType`, extract the single corresponding word or number.
3.  **Handling Missing Data:** If you cannot find a corresponding value for a field in the OCR_TEXT, leave the value in the JSON as its default empty state (e.g., "" for strings, [] for lists). Do not invent or infer data.
4.  **Data Type Formatting:**
    *   Numbers: Where a value is clearly a number (e.g., version number, count, measurements), format it as a JSON number (without quotes). If the value is a mix of numbers and text (e.g., "120MW"), keep it as a string.
    *   Arrays: For fields that expect a list (like `updateDates`), extract all relevant items and format them as a JSON array of strings.
5.  **Special Instruction for Tables (`requiredScope.internalMvCables`):**
    *   Locate the table in the OCR_TEXT that contains columns such as "od", "do", "[km]", "Moc (MVA)", "A", "mm2", etc.
    *   For each data row in that table, create one JSON object within the `internalMvCables` array.
    *   Map the table columns to the JSON object keys as follows:
        *   `from`: The value from the "od" column.
        *   `to`: The value from the "do" column.
        *   `routeLengthKm`: The value from the "[km]" column.
        *   `inverterCount`: The value from a column like "Liczba falowników na stację".
        *   `powerMva`: The value from the "Moc (MVA)" column.
        *   `currentA`: The value from the "A" column.
        *   `conductorCrossSectionMm2`: The value from the first "mm2" column (e.g., Srobocza).
        *   `returnCrossSectionMm2`: The value from the second "mm2" column (e.g., Spowrt).
        *   `coresPerPhase`: The value from the "szt." column.
    *   Ensure all numerical values in the table are converted to JSON numbers.

Output Format:
Your final output must be ONLY the populated JSON object. Do not include any explanations, introductions, apologies, or any other conversational text. The output must be a valid, raw JSON string that can be parsed directly by an application.
```

#### 7.3. `.env` File
Create a `.env` file for local development with the following structure:
```
OPENAI_API_KEY="your_openai_api_key_here"
ANTHROPIC_API_KEY="your_anthropic_api_key_here"
GOOGLE_API_KEY="your_google_api_key_here"
```

### 8. Out of Scope

*   **User Interface (UI):** This is a command-line-only application.
*   **Web API/Service:** The tool will not be exposed as a web service.
*   **LLM Fine-Tuning:** The project will use pre-trained, general-purpose LLM APIs.
*   **Automated Source Citation (Field-level):** The system will not pinpoint the exact page/line for each extracted value.

### 9. Success Metrics

*   **Efficiency Gain:** Reduction in time required to fill out an offer form by at least 75% compared to the manual process.
*   **Accuracy:** >95% of fields are populated correctly (without requiring manual correction) on a sample set of documents.
*   **Reliability:** The application completes a run on a standard project folder without crashing or requiring developer intervention.