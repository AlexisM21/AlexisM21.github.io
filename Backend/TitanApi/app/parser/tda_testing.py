from dotenv import load_dotenv
import os

load_dotenv()

def main():
    pdf_path = "sample_tda.pdf"  # TODO: change this to your actual PDF path

    if not os.path.exists(pdf_path):
        print(f"PDF not found at: {pdf_path}")
        return

    # TODO: replace this with real PDF → text logic
    print("Pretend I just read the PDF!")
    print("Now I would send it to OpenAI or parse it...")

if __name__ == "__main__":
    main()