# Automatic Invoice Maker and Sender

Uses a script + GH actions to take a google sheet of hours worked and automatically generate an invoice and send it to appropriate parties on the first of every month.

## Setup

1. Fork this repo.
2. Save your [timesheet](https://docs.google.com/spreadsheets/d/1ookllAe7kdUx_05QGLUvvp1ZsJM0oVS5P6dyA1awAaE/) in the format shown in google sheets (keep column names as they are) and make it publicly viewable. Edit `make-invoice.py` and set the constant `TIMESHEET` to the url of your timesheet, making sure it is formatted exactly like `https://docs.google.com/spreadsheets/d/1ookllAe7kdUx_05QGLUvvp1ZsJM0oVS5P6dyA1awAaE/` and doesn't have `edit?usp=sharing` at the end. 
3. Create an [app password](https://support.google.com/accounts/answer/185833#zippy=%2Cwhy-you-may-need-an-app-password) for your gmail.
4. In your github repo settings (under "secrets and variables: actions") add two repository secrets: `EMAIL_USERNAME` (your email address), and `EMAIL_PASSWORD` (the app password you created in step 3).

## Testing

Click "Actions" at the top. In the "Actions" column on the left of the resulting screen there will be a "Send Monthly Invoice" workflow. Click on that and then on the right you will see a button that says "run workflow". If you don't want to send your invoice to everyone during the testing you should first edit the relevant `recipients` variable in `make-invoice.py`.
