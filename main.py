from fastapi import FastAPI
from annotation_editor import AnnotationForm

# Load the PDF
app = FastAPI()


form_pdf = AnnotationForm("irs_f1040.pdf", "irs_f1040", 2024, "2024") # 2024

form_pdf.update_field_by_anotation_id_and_page_number(
    "topmostSubform[0].Page1[0].f1_01[0]", 
    1, {
        "default_value": "Feb" , 
        "label": "month",
        "position": {
            "x": 226,
            "y": 62,
            "width": 76,
            "height": 12,
            "unit": "pt"
        },
        "formatting": {
            "font_size": 12,
            "font_family": "Arial",
            "alignment": "left",
            "max_length": 100,
        }
    }
)

# form_pdf.load_updated_annotaion_json("annotation_output.json")

# form_pdf.print_summary()
# output = form_pdf.export_to_json()
# # with open("anontation_output.json", "w") as f:
# #     f.write(output)

form_pdf.save_pdf()

if __name__ == '__main__':
    print("Testing the annotation form")