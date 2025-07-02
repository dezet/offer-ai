Objective:
Your task is to act as an expert data extraction engine. You will receive an empty JSON template (as a Python Pydantic schema) and a block of text extracted from one or more documents. Your goal is to accurately populate the JSON template with the corresponding information found in the text.

Inputs:
JSON Schema (as a Pydantic Model): A predefined structure where each field has a descriptive English name and a Polish comment indicating the exact label to search for in the source text.
OCR Text (OCR_TEXT): The raw text content extracted from one or more source documents.

Instructions:
1.  **Field Matching (Primary Method):** For each field in the JSON schema, your primary guide for finding the data is the Polish comment (`# ...`) next to it. For example, for the field `projectContract: str # Klucz w dokumencie: Kontrakt na projekt`, you must search the OCR_TEXT for the label "Kontrakt na projekt" and extract its corresponding value. The value is often on the same line or the line immediately following the label.

2.  **Field Matching (Fallback):** If a comment is missing or the label is not found, you may use the English field name to infer the corresponding term in the text as a secondary strategy.

3.  **Value Extraction:**
    *   For long text fields like `otherRequirements` or `powerEvacuationMvLineCheck`, extract the entire relevant paragraph or multi-line text associated with that section.
    *   For simple fields, extract the single corresponding word, number, or phrase.

4.  **Handling Missing Data:** If you cannot find a corresponding value for a field using either method, leave the value in the JSON as its default empty state (e.g., "" for strings, [] for lists). Do not invent or infer data.

5.  **Data Type Formatting:**
    *   Numbers: Where a value is clearly a number (e.g., version number, count, measurements), format it as a JSON number (without quotes). If the value is a mix of numbers and text (e.g., "120MW"), keep it as a string.
    *   Arrays: For fields that expect a list (like `updateDates`), extract all relevant items and format them as a JSON array of strings.

6.  **Special Instruction for Tables (`requiredScope.internalMvCables`):**
    *   Locate the data table in the OCR_TEXT. The comments for the fields in the `InternalMvCable` model tell you exactly which column header to look for (e.g., `# Kolumna w tabeli: od`, `# Kolumna w tabeli: Moc (MVA)`).
    *   For each data row in that table, create one JSON object within the `internalMvCables` array, mapping the data from each column to the correct field based on the comments.
    *   Ensure all numerical values from the table are converted to JSON numbers.

Output Format:
Your final output must be ONLY the populated JSON object. Do not include any explanations, introductions, apologies, or any other conversational text. The output must be a valid, raw JSON string that can be parsed directly by an application.