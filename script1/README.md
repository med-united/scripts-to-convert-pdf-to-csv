# Script 1

This script - [script1.py](https://github.com/med-united/scripts-to-convert-pdf-to-csv/blob/main/script1/script1.py) - converts medication statement PDFs with the following structure (with one or more pages):

![medication statement PDF page 1](https://github.com/med-united/scripts-to-convert-pdf-to-csv/blob/main/script1/medication-statement-example-page1.png)

![medication statement PDF page 2](https://github.com/med-united/scripts-to-convert-pdf-to-csv/blob/main/script1/medication-statement-example-page2.png)

## How to run

The medication statements PDFs should be in the same folder as the script. The script will go through all of them and generate:
**1)** one CSV file for each of the PDFs in the folder;
**2)** one CVS file with the name "all-data.csv" that has the content of all the CSV files generated before, all concatenated into one;

```
python3 script1.py
```

