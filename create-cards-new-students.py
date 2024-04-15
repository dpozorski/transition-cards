import os
import re
import pdfkit
import pandas as pd
from bs4 import BeautifulSoup

curr_dir = os.getcwd()
data_dir = os.path.join(curr_dir, "data")
output_dir = os.path.join(curr_dir, "checklists")
# https://docs.google.com/spreadsheets/d/1DuF8djRF3HI6LZLpzSDGdC-xM5RhMgnOi77Gf1jjgL4/edit#gid=0

gender_colors = {
    "M": "#bfffb9",
    "F": "#faff58",
    "NB": "#f4f2f2"
}

race_label_offset = {
    "W": "top: 78px; left: 424px;",
    "B": "top: 76px; left: 436px;",
    "A": "top: 76px; left: 434px;",
    "M": "top: 77px; left: 430px;",
    "W/L": "top: 77px; left: 386px;",
    "M/L": "top: 76px; left: 389px;",
    "B/L": "top: 76px; left: 395px;",
    "W/A": "top: 76px; left: 381px;",
    "W/B": "top: 76px; left: 384px;"
}

flag_colors = {
    "iep": "green",
    "child_study": "#563ffb",
    "ell": "#f4ae39",
    "behavioral_social": "red"
}

options = {
    'page-size': 'Letter',
    'orientation': 'portrait',
    'page-width': '8.5in',
    'page-height': '5.5in',
    'margin-top': '0.0in',
    'margin-right': '0.0in',
    'margin-bottom': '0.0in',
    'margin-left': '0.0in',
    'encoding': "UTF-8",
    'no-outline': None
}

field_mapping = {
    "name": "{{ NAME }}",
    "program": "{{ PROGRAM }}",
    "siblings": "{{ SIBLINGS }}",
    "montessori_experience": "{{ EXPERIENCE }}",
    "grade": "{{ GRADE }}",
    "birthday": "{{ DOB }}",
    "age": "{{ AGE }}",
    "gender": "{{ GENDER_COLOR }}",
    "race": "{{ RACE }}",
    "iep": None,
    "child_study": None,
    "ell": None,
    "behavioral_social": None
}

with open("transition-card-new-students.html") as fp:
    template = BeautifulSoup(fp, 'html.parser')

for fn in os.listdir(data_dir):
    bn = os.path.basename(fn)
    bn_details = bn.split('.')

    if (len(bn_details) == 2) and (bn_details[1] == 'csv'):
        fp = os.path.join(data_dir, fn)
        context = bn_details[0].replace('transition-skills-', '')
        sub_output_dir = os.path.join(output_dir, context)
        df = pd.read_csv(fp)

        if len(df.columns) == 21:
            if not os.path.exists(sub_output_dir):
                os.mkdir(sub_output_dir)

            records = df.to_dict('records')

            for record in records:
                name = None
                worksheet = template.__copy__()

                for key, target in field_mapping.items():
                    if key == "gender":
                        k2 = record[key] if key in record.keys() else "NB"
                        value = gender_colors[k2]

                        for tag in worksheet.findAll(attrs={'class': 'right-border-indicator'}):
                            tag['style'] += "background-color: {};".format(value)
                    elif key in ["iep", "child_study", "ell", "behavioral_social"]:
                        value = record[key] if key in record.keys() else None
                        border_style = "dotted" if value == 2 else "solid"
                        k2 = record["gender"] if "gender" in record.keys() else "NB"
                        border_color = gender_colors[k2] if value == 0 else flag_colors[key]

                        for tag in worksheet.findAll(attrs={'class': key}):
                            tag['style'] += "border-color: {}; border-style: {}".format(border_color, border_style)
                    else:
                        name = record[key] if key == "name" else name
                        value = record[key] if key in record.keys() else None
                        matches = worksheet.find_all(text=re.compile(r'{}'.format(target)))

                        for v in matches:
                            v.replace_with(v.replace(target, str(value)))

                        if key == "race":
                            offset = race_label_offset[value] if value in race_label_offset.keys() else ""

                            for tag in worksheet.findAll(attrs={'class': 'race'}):
                                tag['style'] += offset

                output_file_path = os.path.join(sub_output_dir, name.strip() + ".pdf")
                pdfkit.from_string(str(worksheet), output_file_path, options=options)
