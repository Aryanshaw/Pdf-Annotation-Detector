# PDF Form Annotator (AnnotationForm)

A simple, developer-friendly Python tool to **read, update, and manage form field annotations in PDFs**.  
Built using `PyMuPDF` (`fitz`) with clean data models and JSON-based field control.

---

## 🚀 Features

- ✅ Read and parse form fields from any fillable PDF.
- ✅ Update field values using annotation IDs, labels, or page numbers.
- ✅ Manage formatting: font, alignment, and position (x/y/width/height).
- ✅ Export and import annotations as JSON.
- ✅ Generate annotated PDFs for downstream use.

---

## 📦 Prerequisites

```bash
pip install pymupdf
pip install -r requirements.txt
```

## Methods

AnnotationForm reads and parses the pdf as soon as it is instantiated.

### Read PDF

```python
from annotation_form import AnnotationForm

form = AnnotationForm(pdf_path="path/to/pdf", name="form_name", year=2022, version="1.0")
```

### Update Field

```python
# Update field value by annotation id
form.update_field_by_anotation_id_and_page_number(annotation_id="field_1", page_number=1, field_value={
    "default_value": "new_value",
    "label": "New Label",
    "position": {
        "x": 100,
        "y": 100,
        "width": 100,
        "height": 100,
        "unit": "pt"
    },
    "formatting": {
        "font_size": 10,
        "font_family": "Arial",
        "alignment": "left",
        "max_length": 100,
        "pattern": "",
        "required": False
    }
})

# Update field value by label
form.update_field_by_label_and_page_number(label="field_1_name", page_number=1, field_value={
    "default_value": "new_value",
    "label": "New Label",
    "position": {
        "x": 100,
        "y": 100,
        "width": 100,
        "height": 100,
        "unit": "pt"
    },
    "formatting": {
        "font_size": 10,
        "font_family": "Arial",
        "alignment": "left",
        "max_length": 100,
        "pattern": "",
        "required": False
    }
})
```

### Export Annotations

```python
form.export_to_json()
```

### Load Annotations

```python
form.load_updated_annotaion_json(json_path="path/to/json")
```

### Save PDF

```python
form.save_pdf(output_path="path/to/output.pdf")
```

## AnnotationForm Class

### Properties

| Property | Type          | Description                     |
| -------- | ------------- | ------------------------------- |
| pdf_path | str           | Path to the PDF file.           |
| name     | str           | Name of the PDF form.           |
| year     | int           | Year of the PDF form.           |
| version  | str           | Version of the PDF form.        |
| doc      | fitz.Document | PyMuPDF document object.        |
| pages    | List[Pages]   | List of pages with annotations. |

### Methods

| Method                                                                                                                  | Description                                                           |
| ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| print_summary()                                                                                                         | Prints a summary of the extracted annotations.                        |
| export_to_json()                                                                                                        | Exports the annotations to JSON.                                      |
| update_field_by_anotation_id_and_page_number(annotation_id:str, page_number:int, field_value: Union[UpdateField, dict]) | Updates the field value for a specific annotation id and page number. |
| update_field_by_label_and_page_number(label:str, page_number:int, field_value: Union[UpdateField, dict])                | Updates the field value for a specific label and page number.         |
| load_updated_annotaion_json(json_path:str)                                                                              | Loads the updated annotation json.                                    |
| save_pdf(output_path:Optional[str] = None)                                                                              | Saves the updated PDF.                                                |

### 🧠 About the Author

I am Aryan shaw , Software Developer (https://aryan-shaw.vercel.app).
Built as part of a full-stack assignment for instead + tax pdf file annotation detection.
Feel free to reach out for improvements, feedback, or integration help.
