import streamlit as st
import json
import os
from dotenv import load_dotenv
import smtplib
import email.message
from PIL import Image
import re
from streamlit_js_eval import streamlit_js_eval
import csv
import base64



load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
SMTP_HOST= os.getenv('SMTP_HOST')
SMTP_PORT= os.getenv('SMTP_PORT')
TO_EMAIL= os.getenv('EMAIL_TO')
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

with open('config.json', 'r') as f:
    config = json.load(f)


with open("email_templates.json", "r") as f:
    templates = json.load(f)

def set_bg_hack_url(url):
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url({url});
             background-size: contain; /* Adjust background size to fit the image without cropping */
             background-repeat: no-repeat; /* Prevent image from repeating */
             background-position: center; /* Center the background image */
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

def display_centered_local_image(image_path):
    circle_size=150
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode()
    st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{image_base64}" alt="image" style="width:{circle_size}px; height:{circle_size}px; border-radius: 50%;"></div>', unsafe_allow_html=True)


def are_required_fields_filled(selected_form, form_data):
    unfilled_fields = []
    for field in selected_form['fields']:
        if field.get('required') == "true":
            field_label = field['label']
            if form_data.get(field_label) in (None, ''):
                unfilled_fields.append(field_label)
    return len(unfilled_fields) == 0, unfilled_fields

def validate_gmail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
    return bool(re.match(pattern, email))


def get_countries():
    with open('dialing_codes.json', 'r') as f:
        dialing_codes = json.load(f)
    country_list = [{'name': country, 'code': dialing_codes[country]} for country in dialing_codes]
    return country_list


def send_mail(Content, subject):
    try:
        msg = email.message.Message()
        to_send = ""
        msg['FROM'] =  EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = f'{subject}'
        print(msg.get('Subject'))
        if subject == "Student Registration Form":
            a = templates[subject]
            to_send = a["message"].format(Content["Name"])  
        elif subject == "Patient Registration Form":
            a = templates[subject]
            to_send = a["message"].format(Content["Name"], Content["Doctor's Name"])
        elif subject == "Error in Form Submission":
            a = templates[subject]
            to_send = a['message'].format(Content)
        msg.add_header("Content-Type", 'text/html')
        msg.set_payload(f'{to_send}')
        smtp = smtplib.SMTP(SMTP_HOST,SMTP_PORT)
        smtp.starttls()
        smtp.login(EMAIL,EMAIL_PASSWORD)
        smtp.sendmail(msg['From'], [msg['To']], to_send)
        smtp.quit()
        print("Succesfully send")
    except Exception as e:
        st.write("Error: cannot send mail")

# def format_data(data):
#     formatted_data = ""
#     for key, value in data.items():
#         formatted_data += f"{key}: {value}\n"
#     return formatted_data

def save_to_csv(data, form_type):
    filename = f"{form_type}_data.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:  # Check if file doesn't exist, if so, write header
            writer.writeheader()
        writer.writerow(data)

def submit_form(data, form_type):
    try:
        formatted_data = data
        send_mail(formatted_data, form_type)
        save_to_csv(formatted_data, form_type)
        st.success("Form submitted successfully!")
    except Exception as e:
        st.error(f"Error submitting form: {str(e)}")
        send_mail(str(e), "Error in Form Submission")

def main():

    form_options = [form_name for form_name in config['forms'].keys() if form_name is not None]
    
    form_choice = st.selectbox("Choose Form", form_options)
    
    if form_choice != "None":
        selected_form = config['forms'].get(form_choice)

        
        avatar_image_path = ""
        if selected_form['form_name'] == "Student Registration Form":
            avatar_image_path = "E:\Palm mind\student_avatar.jpg"
            set_bg_hack_url("https://t4.ftcdn.net/jpg/02/76/15/85/360_F_276158586_h5RkwIgMQhvW1mfi7dNPV2GW1NGg3Fvb.jpg")
            
        elif selected_form['form_name'] == "Patient Registration Form":
            avatar_image_path = "E:\Palm mind\patient_avatar.jpeg"
            set_bg_hack_url("https://i.pinimg.com/originals/f1/26/3e/f1263e13c4c02903b41bf80a0033cdbf.jpg")

        if avatar_image_path:
            display_centered_local_image(avatar_image_path)

        st.title(config['chatbot_title'])

        
        st.subheader(selected_form['form_name'])

        form_data = {}

        for field in selected_form['fields']:
            if field['required']=="true":
                field['label'] = field['label'] + " (Required)"
            else:
                pass
            if field['type'] == 'text':
                field_value = st.text_input(field['label'])
            elif field['type'] == 'dropdown':
                field_value = st.selectbox(field['label'], field['options'])
            elif field['type'] == "radio":
                field_value = st.radio(field['label'], field['options'])
            elif field['type'] == "checkbox":
                field_value = st.multiselect(field['label'], field['options'])
            elif field['type'] == "phone":
                country_list = get_countries()
                selected_country = st.selectbox("Select Country Code for Phone number", country_list, format_func=lambda x: f"{x['name']} (+{x['code']})")
                country_code = selected_country['code']
        
                # Display combined country code and phone number input field
                phone_number_with_code = st.text_input("Phone Number (including country code)", value=f"+{country_code}")
        
                # Example of extracting country code and phone number
                if phone_number_with_code.startswith(f"+{country_code}"):
                    phone_number = phone_number_with_code[len(f"+{country_code}"):]
                    field_value = country_code + phone_number

            elif field['type'] == "gmail":
                field_value = st.text_input(field['label'])

                if not validate_gmail(field_value):
                    st.warning("Please enter a valid Gmail address.")
            
            elif field['type'] == "date":
                field_value = st.date_input(field['label'])
            
            elif field['type'] == "insurance":
                field_value = st.radio(field['label'], field['options'])

                if field_value == "Yes":
                    with open('insurance.json', 'r') as f:
                        insurance_data = json.load(f)

                    insurance_form_data = {}

                    st.title("Insurance Form")


                    for fields in insurance_data['fields']:
                        if fields['type'] == 'text':
                            my_field_value = st.text_input(fields['label'])
                        elif fields['type'] == 'radio':
                            my_field_value = st.radio(fields['label'], fields['options'])
                        
                        insurance_form_data[fields['label']] = my_field_value
                    
                    field_value = insurance_form_data
                    if field['required']=="true":
                        field['label'] = field['label'].split(" (Required)")[0]
                    else:
                        pass

            form_data[field['label']] = field_value

        all_fields_filled, unfilled_fields = are_required_fields_filled(selected_form, form_data)
        if st.button("Submit",disabled=not all_fields_filled):
            if all_fields_filled:
                submit_form(form_data, selected_form['form_name'])
            else:
                st.warning(f"Please fill out the required fields: {', '.join(unfilled_fields)}")

        if st.button("Cancel"):
            st.warning("You have canceled your form application")
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
        
        st.warning("Submit button disabled until all required fields are filled")


if __name__ == "__main__":
    main()
