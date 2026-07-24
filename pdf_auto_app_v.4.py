import streamlit as st
from pypdf import PdfReader, PdfWriter, PageObject
from datetime import datetime
from io import BytesIO

# App title
st.title("PDF Letterhead Overlay Tool")
st.markdown("""
This tool overlays a fixed letterhead on every page of a multi-page report.
Select the report format, upload your report, and generate the final PDF.
""")

# Fixed PDF Paths
FIXED_LETTERHEAD_PATH = "App Letterhead.pdf"
#FIRST_PAGE_PATH = "first page.pdf"
LAST_PAGE_PATH = "final page app.pdf"

# Load required PDFs
try:
    # Letterhead
    letterhead_reader = PdfReader(FIXED_LETTERHEAD_PATH)
    letterhead_page = letterhead_reader.pages[0]

    # First Page
    #first_page_reader = PdfReader(FIRST_PAGE_PATH)

    # Last Page
    last_page_reader = PdfReader(LAST_PAGE_PATH)

except Exception as e:
    st.error(f"Failed to load required PDF files.\n\n{e}")
    st.stop()

# Quro ID input
number_part = st.text_input("Enter the numeric part of Quro ID (e.g., 123)")
quro_id = f"QC{number_part}" if number_part.isdigit() else None

if number_part:
    if not number_part.isdigit():
        st.error("Invalid input! Please enter only the numeric part of the Quro ID.")
        quro_id = None

# Report format
report_format = st.selectbox(
    "Select the report format",
    ["Select format", "LPL / MTT", "MP"]
)

if report_format != "Select format":

    # Upload report
    report_file = st.file_uploader("Upload Report PDF", type=["pdf"])

    if report_file and quro_id:

        try:

            report_reader = PdfReader(report_file)

            output_pdf = PdfWriter()

            # --------------------------------------------------
            # Add Fixed First Page(s)
            # --------------------------------------------------
            #for page in first_page_reader.pages:
                #output_pdf.add_page(page)

            # --------------------------------------------------
            # Process Report Pages
            # --------------------------------------------------
            for report_page in report_reader.pages:

                new_page = PageObject.create_blank_page(
                    width=letterhead_page.mediabox.width,
                    height=letterhead_page.mediabox.height
                )

                # LPL / MTT
                if report_format == "LPL / MTT":

                    new_page.merge_page(letterhead_page)
                    new_page.merge_page(report_page)

                # MP
                elif report_format == "MP":

                    content_width = report_page.mediabox.width
                    content_height = report_page.mediabox.height

                    available_width = letterhead_page.mediabox.width
                    available_height = letterhead_page.mediabox.height - 160

                    scale_x = available_width / content_width
                    scale_y = available_height / content_height
                    scale_factor = min(scale_x, scale_y)

                    translate_x = (
                        available_width - (content_width * scale_factor)
                    ) / 2

                    translate_y = 60

                    report_page.add_transformation([
                        scale_factor,
                        0,
                        0,
                        scale_factor,
                        translate_x,
                        translate_y
                    ])

                    new_page.merge_page(letterhead_page)
                    new_page.merge_page(report_page)

                output_pdf.add_page(new_page)

            # --------------------------------------------------
            # Add Fixed Last Page(s)
            # --------------------------------------------------
            for page in last_page_reader.pages:
                output_pdf.add_page(page)

            # --------------------------------------------------
            # Create Download File
            # --------------------------------------------------
            output_pdf_stream = BytesIO()
            output_pdf.write(output_pdf_stream)
            output_pdf_stream.seek(0)

            current_date = datetime.now().strftime("%Y-%b-%d")

            st.download_button(
                label="Download Final PDF",
                data=output_pdf_stream,
                file_name=f"Qurocare_Lab_Report_{quro_id}_{current_date}.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"An error occurred while processing the PDF:\n\n{e}")
