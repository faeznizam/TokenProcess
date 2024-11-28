***Purpose***: 

The goal of this project is to streamline and automate the file preparation and data mapping process for tokenization, which is currently manual and time-consuming. By automating key steps, the process will become more efficient, reduce human errors, and improve overall workflow. This optimization will minimize manual interventions, ensure consistency, and expedite the preparation and updating of tokenization files, ultimately enhancing productivity and accuracy in data handling.


***Current Process***:
1. Start with an Excel file (.xlsx) containing data for tokenization.
2. Manually copy and paste data into a template file.
3. Generate a batch ID for the file.
4. Manually populate required fields based on the data.
5. Save the file as .csv and send it via the client portal.
6. Receive a .csv file returned from the client portal.
7. Map the data from the .csv file to the original .xlsx file using the phone number as the key.
8. Manually copy and paste the mapped data into the original file.
9. Update the data in the database via SFTP.


***Optimized Process***:
1. Automate steps 1-4 using Python.
2. Send the file via the client portal.
3. Receive the returned file.
4. Automate steps 7-8 using Python.
5. Update the data in the database via SFTP.


