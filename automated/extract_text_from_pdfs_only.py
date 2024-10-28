import os
import fitz  # PyMuPDF
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().handlers = [console_handler] 

failed_pdf_log = "failed_pdf_extraction_files.txt"

def extract_text_from_pdf(pdf_path, txt_path):
    """
    Extract text from a PDF and save it to a text file.
    :param pdf_path: Path to the PDF file.
    :param txt_path: Path to save the extracted text.
    """
    try:
        logging.debug(f"Opening PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        text = ""
        for page_number in range(len(doc)):
            logging.debug(f"Extracting text from page {page_number + 1} of {pdf_path}")
            page = doc.load_page(page_number)
            text += page.get_text()
        doc.close()

        logging.debug(f"Saving extracted text to: {txt_path}")
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        # Successfully extracted; remove from failed list if it was there
        remove_from_failed_list(pdf_path)

    except Exception as e:
        logging.error(f"Failed to extract text from {pdf_path}: {e}")
        add_to_failed_list(pdf_path)


def add_to_failed_list(pdf_path):
    """Add a PDF path to the failed extraction list if not already present."""
    with open(failed_pdf_log, "a+") as f:
        f.seek(0)
        failed_files = f.read().splitlines()
        if pdf_path not in failed_files:
            f.write(f"{pdf_path}\n")


def remove_from_failed_list(pdf_path):
    """Remove a PDF path from the failed extraction list."""
    if not os.path.exists(failed_pdf_log):
        return

    with open(failed_pdf_log, "r") as f:
        failed_files = f.read().splitlines()

    if pdf_path in failed_files:
        failed_files.remove(pdf_path)

    with open(failed_pdf_log, "w") as f:
        f.writelines(f"{file}\n" for file in failed_files)


def process_pdfs_recursively(folder_path):
    """
    Recursively process all PDFs in a directory, extracting text from each.
    :param folder_path: Root directory to start the search.
    """
    # Check and retry previously failed PDFs
    if os.path.exists(failed_pdf_log):
        with open(failed_pdf_log, "r") as f:
            failed_files = f.read().splitlines()
        for pdf_path in failed_files:
            txt_path = os.path.join(os.path.dirname(pdf_path), "txt_content_from_pdf_extracted.txt")
            logging.info(f"Retrying failed PDF: {pdf_path}")
            extract_text_from_pdf(pdf_path, txt_path)

    # Process new PDFs in the folder structure
    for root, _, files in os.walk(folder_path):
        txt_path = os.path.join(root, "txt_content_from_pdf_extracted.txt")
        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            logging.info(f"Text content already extracted in directory: {root}. Skipping...")
            continue  # Skip processing this directory if extracted content already exists

        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                logging.info(f"Processing PDF: {pdf_path}")
                extract_text_from_pdf(pdf_path, txt_path)


if __name__ == "__main__":
    # Specify the root folder containing the PDFs
    root_folder = "..\\Intel Reports\\"
    logging.info(f"Starting PDF extraction in folder: {root_folder}")
    process_pdfs_recursively(root_folder)
    logging.info("PDF extraction process completed.")


# add function to extract text from images in addition to text (some reports are only images...)