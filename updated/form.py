import streamlit as st
import json
import os
from dotenv import load_dotenv
import smtplib
import email.message
from PIL import Image
import re


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
        msg['Subject'] = f"{subject}"
        msg['FROM'] =  EMAIL
        msg['To'] = TO_EMAIL
        msg.add_header("Content-Type", 'text/html')
        msg.set_payload(f'{Content}')
        smtp = smtplib.SMTP(SMTP_HOST,SMTP_PORT)
        smtp.starttls()
        smtp.login(EMAIL,EMAIL_PASSWORD)
        smtp.sendmail(msg['From'], [msg['To']], msg.as_string())
        smtp.quit()
        print("Succesfully send")
    except Exception as e:
        st.write("Error: cannot send mail")

def format_data(data):
    formatted_data = ""
    for key, value in data.items():
        formatted_data += f"{key}: {value}\n"
    return formatted_data

def submit_form(data, form_type):
    try:
        formatted_data = format_data(data)
        send_mail(formatted_data, f"{form_type} Submission")
        st.success("Form submitted successfully!")
    except Exception as e:
        st.error(f"Error submitting form: {str(e)}")
        send_mail(str(e), "Error in Form Submission")

def main():

    form_choice = st.selectbox("Choose Form", list(config['forms'].keys()))

    selected_form = config['forms'][form_choice]
    
    avatar_image_path = ""
    if selected_form['form_name'] == "Student Registration Form":
        avatar_image_path = "E:\Palm mind\student_avatar.jpg"
    elif selected_form['form_name'] == "Hospital Registration Form":
        avatar_image_path = "E:\Palm mind\patient_avatar.jpeg"

    if avatar_image_path:
        avatar_image = Image.open(avatar_image_path)
        st.image(avatar_image, width=200)
        st.markdown(
            "<style>img {border-radius: 50%;text-align:center; margin-left: auto; margin-right: auto; display: block}</style>",
            unsafe_allow_html=True
        )

    st.title(config['chatbot_title'])


    # if selected_form['form_name'] == "Student Registration Form":
    #     image = Image.open(r"E:\Palm mind\student_registration_logo.jpg")
    #     st.image(image=image, use_column_width=True)
    # elif selected_form['form_name'] == "Hospital Registration Form":
    #     image = Image.open(r"E:\Palm mind\hospital_logo.png")
    #     st.image(image=image, use_column_width=True)

    
    st.subheader(selected_form['form_name'])

    form_data = {}
    for field in selected_form['fields']:
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
            selected_country = st.selectbox("Select Country", country_list, format_func=lambda x: f"{x['name']} (+{x['code']})")
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


        form_data[field['label']] = field_value

    if st.button("Submit"):
        submit_form(form_data, selected_form['form_name'])

    if st.button("Restart"):
        main()

if __name__ == "__main__":
    main()
