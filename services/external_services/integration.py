import webbrowser
import os
import subprocess

def open_web_browser(url):
    """Open a web browser with the specified URL."""
    webbrowser.open(url)

def open_microsoft_word(file_path):
    """Open a Microsoft Word document."""
    try:
        subprocess.Popen(["start", file_path], shell=True)
    except Exception as e:
        print(f"Error opening Word document: {e}")

def open_excel(file_path):
    """Open a Microsoft Excel spreadsheet."""
    try:
        subprocess.Popen(["start", file_path], shell=True)
    except Exception as e:
        print(f"Error opening Excel file: {e}")

def open_powerpoint(file_path):
    """Open a Microsoft PowerPoint presentation."""
    try:
        subprocess.Popen(["start", file_path], shell=True)
    except Exception as e:
        print(f"Error opening PowerPoint file: {e}")

def open_pdf(file_path):
    """Open a PDF file."""
    try:
        os.startfile(file_path)
    except Exception as e:
        print(f"Error opening PDF file: {e}")

if __name__ == "__main__":
    # Example usage
    open_web_browser("https://www.microsoft.com")
    open_microsoft_word("example.docx")
    open_excel("example.xlsx")
    open_powerpoint("example.pptx")
    open_pdf("example.pdf")