import streamlit as st
from pypdf import PdfReader, PdfWriter, PageObject
from datetime import datetime
from io import BytesIO
import os

# App title
st.title("PDF Letterhead Overlay Tool")
st.markdown("""
This tool overlays a fixed letterhead on every page of a multi-page report. 
Select the report format, upload your report, and generate the final PDF.
""")

# Fixed Letterhead Path (change this to the actual path of your fixed letterhead file)
FIXED_LETTERHEAD_PATH = "letterhead_new_new.pdf"

# Validate the existence of the fixed letterhead
try:
    letterhead_reader = PdfReader(FIXED_LETTERHEAD_PATH)
    letterhead_page = letterhead_reader.pages[0]
except Exception as e:
    st.error("Failed to load the fixed letterhead file. Please check the file path.")
    st.stop()

# Quro ID input field
number_part = st.text_input("Enter the numeric part of Quro ID (e.g., 123)")
quro_id = f"QC{number_part}" if number_part.isdigit() else None

# Validate Quro ID
if number_part:
    if not number_part.isdigit():
        st.error("Invalid input! Please enter only the numeric part of the Quro ID.")
        quro_id = None

# Dropdown to select the report format
report_format = st.selectbox(
    "Select the report format",
    ["Select format", "LPL / MTT", "DS"]
)

if report_format != "Select format":
    # File uploader for the report
    report_file = st.file_uploader("Upload Report PDF", type=["pdf"])

    if report_file and quro_id:
        try:
            # Create PdfReader for the uploaded report
            report_reader = PdfReader(report_file)

            # Create a PdfWriter for the output PDF
            output_pdf = PdfWriter()

            # Process each page of the report
            for report_page in report_reader.pages:
                # Create a new blank page with the dimensions of the letterhead
                new_page = PageObject.create_blank_page(
                    width=letterhead_page.mediabox.width,
                    height=letterhead_page.mediabox.height
                )

                # If the format is LPL, simply overlay the letterhead without scaling
                if report_format == "LPL / MTT":
                    # Merge the letterhead and the report content without scaling
                    new_page.merge_page(letterhead_page)
                    new_page.merge_page(report_page)

                # If the format is DS, apply scaling and overlay the letterhead
                elif report_format == "DS":
                    # Scale down the report content to fit within the adjusted dimensions
                    content_width = report_page.mediabox.width
                    content_height = report_page.mediabox.height
                    available_width = letterhead_page.mediabox.width
                    available_height = letterhead_page.mediabox.height - 160  # Leave space for header/footer

                    # Calculate the scale factor
                    scale_x = available_width / content_width
                    scale_y = available_height / content_height
                    scale_factor = min(scale_x, scale_y)

                    # Calculate the horizontal and vertical translation to center the content
                    translate_x = (available_width - (content_width * scale_factor)) / 2
                    translate_y = 60  # Adjust the bottom margin

                    # Apply transformations to scale and position the content
                    report_page.add_transformation([
                        scale_factor, 0, 0, scale_factor, translate_x, translate_y
                    ])

                    # Merge the letterhead and the scaled report content
                    new_page.merge_page(letterhead_page)
                    new_page.merge_page(report_page)

                # Add the new page to the output PDF
                output_pdf.add_page(new_page)

            # Save the final PDF to a BytesIO object for downloading
            output_pdf_stream = BytesIO()
            output_pdf.write(output_pdf_stream)
            output_pdf_stream.seek(0)

            # Get the current date in YYYY-MMM-DD format
            current_date = datetime.now().strftime("%Y-%b-%d")

            # Provide a download link for the final PDF with Quro ID and date in the file name
            st.download_button(
                label="Download Final PDF",
                data=output_pdf_stream,
                file_name=f"Qurocare_Lab_Report_{quro_id}_{current_date}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"An error occurred while processing the PDF: {e}")
