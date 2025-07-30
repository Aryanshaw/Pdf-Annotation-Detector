import fitz
import json
from dataclasses import dataclass
from typing import List, Optional , Union

@dataclass
class Position:
    x: int
    y: int
    width: int
    height: int
    unit: str

@dataclass
class Formatting:
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    alignment: Optional[str] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    required: Optional[bool] = None

@dataclass
class DataReference:
    path: str
    default_value: Optional[str] = None

@dataclass
class Annotation:
    id: str
    type: str
    position: Position
    formatting: Formatting
    data_reference: DataReference
    label: Optional[str] = None

    def __str__(self):
        return f"{self.type.upper()} | {self.id} | Label: {self.label} | Value: {self.data_reference.default_value}"

@dataclass 
class Pages:
    page_number: int
    annotations: List[Annotation]

@dataclass
class UpdateField:
    default_value: Optional[str] = None
    label: Optional[str] = None
    position: Optional[Position] = None
    formatting: Optional[Formatting] = None

    @classmethod
    def from_dict(cls, data: dict):
        pos = data.get("position")
        fmt = data.get("formatting")

        return cls(
            default_value=data.get("default_value"),
            label=data.get("label"),
            position=Position(**pos) if pos else None,
            formatting=Formatting(**fmt) if fmt else None
        )

class AnnotationForm:
    def __init__(self, pdf_path: str , name:str, year:int, version:str):
        self.pdf_path = pdf_path
        self.name = name
        self.year = year
        self.version = version
        self.doc = None
        self.pages: List[Pages] = []
        self.__read_pdf()

    def __read_pdf(self):
        """Main method to read PDF and extract annotations using PyMuPDF"""
        try:
            doc = fitz.open(self.pdf_path)
            self.doc = doc
            for page_num in range(len(doc)):
                page = doc[page_num]
                annotations = []
                
                # Get form fields (widgets)
                widgets = page.widgets()
                print(f"Page {page_num + 1}: Found widgets")
                
                for widget in widgets:
                    try:
                        field_name = widget.field_name or f"field_{len(annotations)}"
                        field_type = widget.field_type_string or ""
                        field_value = widget.field_value or ""
                        field_label = widget.field_label
                        
                        # Get position
                        rect = widget.rect
                        position = Position(
                            x=int(rect.x0),
                            y=int(rect.y0), 
                            width=int(rect.x1 - rect.x0),
                            height=int(rect.y1 - rect.y0),
                            unit="pt"
                        )
                        
                        # Map field type
                        annotation_type = self.__map_pymupdf_field_type(field_type)
                        
                        annotation = Annotation(
                            id=field_name,
                            type=annotation_type,
                            label=field_label,
                            position=position,
                            formatting=Formatting(8, "Arial", "left", 100, "", False),
                            data_reference=DataReference(field_name, str(field_value))
                        )
                        annotations.append(annotation)
                        
                    except Exception as e:
                        print(f"  Error processing widget: {e}")
                        continue
                
                if annotations:
                    page_obj = Pages(page_number=page_num + 1, annotations=annotations)
                    self.pages.append(page_obj)
            
            doc.close()
            self.doc = None
            
        except Exception as e:
            print(f"Error reading PDF: {e}")
            raise

    def __map_pymupdf_field_type(self, field_type):
        """Map PyMuPDF field types to our annotation types"""
        mapping = {
            "Text": "text",
            "CheckBox": "checkbox",
            "RadioButton": "radio", 
            "ComboBox": "dropdown",
            "ListBox": "list",
            "Signature": "signature"
        }
        return mapping.get(field_type, "text")
    
    def print_summary(self):
        """Print a summary of extracted annotations"""
        total_annotations = sum(len(page.annotations) for page in self.pages)
        print("\n=== PDF Form Analysis Summary ===")
        print(f"PDF: {self.name} (Year: {self.year}, Version: {self.version})")
        print(f"Total Pages: {len(self.pages)}")
        print(f"Total Annotations: {total_annotations}")

        for page in self.pages:
            print(f"\nPage {page.page_number}: {len(page.annotations)} annotations")
            for ann in page.annotations:
                print(f"  - {ann.id} ({ann.type}): '{ann.label}' = '{ann.data_reference.default_value}'")
                print(f"    Position: ({ann.position.x:.1f}, {ann.position.y:.1f}) Size: {ann.position.width:.1f}x{ann.position.height:.1f}")

    def export_to_json(self):
        """Export annotations to JSON format"""
        import json
        
        data = {
            "pdf_info": {
                "name": self.name,
                "year": self.year,
                "version": self.version,
                "path": self.pdf_path
            },
            "pages": []
        }
        
        for page in self.pages:
            page_data = {
                "page_number": page.page_number,
                "annotations": []
            }
            
            for ann in page.annotations:
                ann_data = {
                    "id": ann.id,
                    "type": ann.type,
                    "label": ann.label,
                    "position": {
                        "x": ann.position.x,
                        "y": ann.position.y,
                        "width": ann.position.width,
                        "height": ann.position.height,
                        "unit": ann.position.unit
                    },
                    "formatting": {
                        "font_size": ann.formatting.font_size,
                        "font_family": ann.formatting.font_family,
                        "alignment": ann.formatting.alignment,
                        "max_length": ann.formatting.max_length,
                        "pattern": ann.formatting.pattern,
                        "required": ann.formatting.required
                    },
                    "data_reference": {
                        "path": ann.data_reference.path,
                        "default_value": ann.data_reference.default_value
                    }
                }
                page_data["annotations"].append(ann_data)
            
            data["pages"].append(page_data)
        
        return json.dumps(data, indent=2)
    
    def __find_widget_by_annotation_id(self, page:int, annotation_id:str):
        """Find the widget with the given annotation id"""
        for widget in page.widgets():
            if widget.field_name == annotation_id:
                return widget
            
        return None

    def __find_widget_by_label(self, page:int, label:str):
        """Find the widget with the given label name"""
        for widget in page.widgets():
            if widget.field_label == label:
                return widget
            
        return None

    def update_field_by_anotation_id_and_page_number(self, annotation_id:str, page_number:int, field_value: Union[UpdateField, dict]):
        """Update the field value for a specific annotation id and page number"""
        try:
            if not self.doc:
                doc = fitz.open(self.pdf_path)
                self.doc = doc
            doc = self.doc
            page = doc[page_number -1]

            # find the widget with the given annotation id
            widget = self.__find_widget_by_annotation_id(page, annotation_id)
            if not widget:
                raise Exception(f"Widget with annotation id {annotation_id} not found")

            if isinstance(field_value, dict):
                field_value = UpdateField.from_dict(field_value)

            # update the field value
            if field_value.default_value:
                widget.field_value = field_value.default_value
                widget.update()

            if field_value.position:
                pos = field_value.position
                new_rect = fitz.Rect(pos.x, pos.y, pos.x + pos.width, pos.y + pos.height)
                widget.rect = new_rect
                widget.update()

            # Update formatting if provided
            if field_value.formatting:
                fmt = field_value.formatting
                if fmt.font_size:
                    widget.text_fontsize = fmt.font_size
                if fmt.font_family:
                    widget.text_font = fmt.font_family
                widget.update()

            if field_value.label:
                widget.field_label = field_value.label
                widget.update()
            
            return True
        except Exception as e:
            print(f"Error updating field value: {e}")
            raise
    
    def update_field_by_label_and_page_number(self, label:str, page_number:int, field_value: Union[UpdateField, dict]):
        """Update the field value for a specific label and page number"""
        try:
            if not self.doc:
                doc = fitz.open(self.pdf_path)
                self.doc = doc
            doc = self.doc
            page = doc[page_number -1]

            # find the widget with the given label
            widget = self.__find_widget_by_label(page, label)
            if not widget:
                raise Exception(f"Widget with label {label} not found")

            if isinstance(field_value, dict):
                field_value = UpdateField.from_dict(field_value)

            # update the field value
            if field_value.default_value:
                widget.field_value = field_value.default_value
                widget.update()

            if field_value.position:
                pos = field_value.position
                new_rect = fitz.Rect(pos.x, pos.y, pos.x + pos.width, pos.y + pos.height)
                widget.rect = new_rect
                widget.update()

            # Update formatting if provided
            if field_value.formatting:
                fmt = field_value.formatting
                if fmt.font_size:
                    widget.text_fontsize = fmt.font_size
                if fmt.font_family:
                    widget.text_font = fmt.font_family
                widget.update()

            if field_value.label:
                widget.field_label = field_value.label
                widget.update()
            
            return True
        except Exception as e:
            print(f"Error updating field value: {e}")
            raise

    def load_updated_annotaion_json(self, json_path:str):
        """Load the updated annotation json"""
        try:
            
            with open(json_path, "r") as f:
                updated_annotations_json = json.load(f)
            
            if not updated_annotations_json.get("pages"):
                raise Exception("Invalid updated annotation json")
            
            for page in self.pages:
                for ann in page.annotations:
                    for page in updated_annotations_json.get("pages"):
                        for new_ann in page.get("annotations"):
                            if ann.id == new_ann.get("id"):
                                update_body = {
                                    "default_value": new_ann.get("data_reference").get("default_value"),
                                    "label": new_ann.get("label"),
                                    "position": new_ann.get("position"),
                                    "formatting": new_ann.get("formatting")
                                }
                                self.update_field_by_anotation_id_and_page_number(
                                    ann.id, 
                                    page.get("page_number"), 
                                    update_body
                                )

            return True

        except Exception as e:
            print(f"Error loading updated annotation json: {e}")
            raise

    def save_pdf(self , output_path:Optional[str] = None):
        """Save the updated PDF"""
        if self.doc is not None:
            self.doc.save(output_path or "output.pdf")
            self.doc.close()
   