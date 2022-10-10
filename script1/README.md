# Script 1 to convert PDF medication statement to CSV

This script - [script1.py]() - converts medication statement PDFs with the following structure (with one or more pages):

![medication statement PDF page 1]()

![medication statement PDF page 2]()

## How to run

The medication statements PDFs should be in the same folder as the script. The script will go through all of them and generate:
**1)** one CSV file for each of the PDFs in the folder;
**2)** one CVS file with the name "all-data.csv" that has the content of all the CSV files generated before, all concatenated into one;

```
python3 script1.py
```

