import os
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import pypandoc
import subprocess

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from email.utils import formatdate

# Define the public Google Sheets CSV export link
TIMESHEET_URL = "https://docs.google.com/spreadsheets/d/1ookllAe7kdUx_05QGLUvvp1ZsJM0oVS5P6dyA1awAaE/"
sharing_url = f"{TIMESHEET_URL}edit?usp=sharing"

# Function to generate invoice for a given month
def generate_invoice_md(month, year, hourly_rate=280.00):
    # Load the Google Sheet into a DataFrame
    df = pd.read_csv(f'{TIMESHEET_URL}export?format=csv')
    
    # Convert the Date column to datetime
    df['Date'] = pd.to_datetime(df['Work Date'])
    
    # Filter the dataframe for the given month and year
    df_filtered = df[(df['Date'].dt.month == month) & (df['Date'].dt.year == year)]
    
    if df_filtered.empty:
        print("No records found for the specified month and year.")
        return
    
    total_hours = df_filtered['Hours'].sum()
    total_amount = total_hours * hourly_rate
    
    # Create the Markdown content
    invoice_content = f"""
# Invoice

**Alejandro Schuler**  
alejandro.schuler@gmail.com  
408 799 8150  
360 Coleridge St.  
San Francisco, CA 94110

---

**BILL TO**: DHCS / KPMG

**DATE**: {datetime.datetime.today().strftime("%m/%d/%y")}

**[TIMESHEET LINK]({sharing_url})**

---

## Items

| Date | Description                           | Quantity (hours) | Price per hour | Amount   |
|------|---------------------------------------|------------------|----------------|----------|
"""

    for _, row in df_filtered.iterrows():
        date = row['Work Date']
        description = row['Time Narrative']
        hours = row['Hours']
        amount = hours * hourly_rate
        invoice_content += f"| {date} | {description} | {hours:.2f} | ${hourly_rate:.2f} | ${amount:.2f} |\n"

    invoice_content += f"\n**Total Hours**: {total_hours:.2f}\n\n"
    invoice_content += f"**Hourly Rate**: ${hourly_rate:.2f}\n\n"
    invoice_content += f"## **Total Amount**: ${total_amount:.2f}\n\n"

    output = f"../{year}-{month}"
    md_path = f"{output}.md"
    html_path =f"{output}.html"
    pdf_path =f"{output}.pdf"

    # Write the Markdown content to a file
    with open(md_path, 'w') as md_file:
        md_file.write(invoice_content)
    
    print(f"Markdown file generated: {md_path}")
    
    # Convert Markdown to HTML
    pypandoc.convert_file(
        md_path,
        'html',
        outputfile=html_path
    )

    # Convert Markdown to PDF
    subprocess.run(['wkhtmltopdf', '--enable-local-file-access', html_path, pdf_path])
    print(f"PDF generated: {pdf_path}")

    os.remove(md_path)
    os.remove(html_path)

    return pdf_path


# export EMAIL_USERNAME='test@example.com'
# export EMAIL_PASSWORD='supersecretpassword'
def send_email_with_pdf(pdf_path, subject, body, recipients):
    sender_email = os.environ['EMAIL_USERNAME']
    sender_password = os.environ['EMAIL_PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(body))

    with open(pdf_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(pdf_path)))
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())


def get_last_month_and_year():
    # Get today's date
    today = datetime.datetime.today()
    
    # Subtract one month from today's date
    last_month_date = today - relativedelta(months=1)
    
    # Extract the month and year as integers
    last_month = last_month_date.month
    last_year = last_month_date.year
    
    return last_month, last_year


# Main entry point for the script
if __name__ == "__main__":
    month, year = get_last_month_and_year()

    subject = f"Invoice {year}-{month}"
    body = f"Please find the attached invoice for this month. The weekly timesheet is here: {sharing_url}."
    recipients = [
        "alejandro.schuler@gmail.com", 
        # "jennifer.pongonis@pme-indy.com",
        # "priyankasrinivasan@kpmg.com",
        # "cnowlin@pme-indy.com",
        # "dbahnsen@pme-indy.com",
        # "kkessel@kpmg.com",
        # "John.Scott@dhcs.ca.gov"
    ]

    pdf_path = generate_invoice_md(month=month, year=year)
    send_email_with_pdf(pdf_path, subject, body, recipients)