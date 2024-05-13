from openai import OpenAI
import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.title("Xenium Airbot")

client = OpenAI(api_key="")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load flight details from Excel sheet
flight_details_df = pd.read_excel("flight_data.xlsx")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "show the flight details" in prompt.lower():
        with st.chat_message("assistant"):
            st.write("Here are the available flights:")
            st.write(flight_details_df)
    elif "book the flight" in prompt.lower():
        st.session_state.user_info = {}
        st.session_state.user_info["booking_stage"] = "collect_info"
    else:
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

if "user_info" in st.session_state:
    if st.session_state.user_info.get("booking_stage") == "collect_info":
        with st.expander("Flight Booking Details"):
            st.write("Please enter the following details for flight booking:")
            passenger_name = st.text_input("Passenger Name")
            age = st.number_input("Age", min_value=1, max_value=150, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            departure_place = st.text_input("Departure Place")
            arrival_place = st.text_input("Arrival Place")
            date = st.date_input("Date")
            aadhar_number = st.text_input("Aadhar Number")
            selected_flight_id = st.selectbox("Select Flight by Flight ID", flight_details_df["Flight ID"])
            num_adults = st.number_input("Number of Adults", min_value=1, max_value=10, step=1)
            num_children = st.number_input("Number of Children", min_value=0, max_value=10, step=1)

        if st.button("Confirm Booking"):
            st.session_state.user_info.update({
                "passenger_name": passenger_name,
                "age": age,
                "gender": gender,
                "departure_place": departure_place,
                "arrival_place": arrival_place,
                "date": date,
                "aadhar_number": aadhar_number,
                "selected_flight_id": selected_flight_id,
                "num_adults": num_adults,
                "num_children": num_children
            })
            st.session_state.user_info["booking_stage"] = "confirm_booking"
        elif st.button("Cancel"):
            st.session_state.user_info.clear()

if "user_info" in st.session_state:
    if st.session_state.user_info.get("booking_stage") == "confirm_booking":
        with st.expander("Confirm Booking"):
            st.write("Please confirm the following booking details:")
            st.write("Passenger Name:", st.session_state.user_info["passenger_name"])
            st.write("Age:", st.session_state.user_info["age"])
            st.write("Gender:", st.session_state.user_info["gender"])
            st.write("Departure Place:", st.session_state.user_info["departure_place"])
            st.write("Arrival Place:", st.session_state.user_info["arrival_place"])
            st.write("Date:", st.session_state.user_info["date"])
            st.write("Aadhar Number:", st.session_state.user_info["aadhar_number"])
            st.write("Selected Flight ID:", st.session_state.user_info["selected_flight_id"])
            st.write("Number of Adults:", st.session_state.user_info["num_adults"])
            st.write("Number of Children:", st.session_state.user_info["num_children"])
        
        if st.button("Make Payment"):

        if st.button("Confirm"):
            # Generate PDF ticket with professional background
            def create_ticket_pdf(user_info):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=14)
    
                # Add professional background
                pdf.image("professional_background.jpg", x=0, y=0, w=210, h=297)

                # Write ticket details
                pdf.cell(200, 60, txt="", ln=True, align="C")
                for key, value in user_info.items():
                    pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value}", ln=True)

                pdf_filename = f"ticket_{user_info['passenger_name']}.pdf"
                pdf_output_path = f"./{pdf_filename}"  # Save PDF in the current directory

                pdf.output(pdf_output_path)
                return pdf_output_path, pdf_filename

            pdf_output_path, pdf_filename = create_ticket_pdf(st.session_state.user_info)

            # Provide the generated PDF as a download
            st.download_button(
                label="Download Ticket",
                data=open(pdf_output_path, "rb").read(),
                file_name=pdf_filename,
                mime="application/pdf"
            )

            # Delete the PDF file after download
            if os.path.exists(pdf_output_path):
                os.remove(pdf_output_path)
        elif st.button("Cancel"):
            st.session_state.user_info.clear()
