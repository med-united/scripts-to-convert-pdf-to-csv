import re
import tabula
import glob
import requests
import json
import pandas as pd

from PyPDF2 import PdfReader

def getMedicationPZN(medicationName, medicationWirkstoffe, medicationForm):
	print("\nMedication name to look for: ", medicationName)
	print("Medication wirkstoffe to look for: ", medicationWirkstoffe)
	print("Medication form to look for: ", medicationForm)

	medicationToLookup = str(medicationName).lower().strip().replace(" ", "-")
	medicationToLookup = medicationToLookup.replace("/", "-")
	medicationToLookup = medicationToLookup.replace(".", "")
	formToLookup = str(medicationForm).lower().strip()
	formToLookup = formToLookup.replace(".", "")
	formToLookup = formToLookup.replace(" ", "-")

	query1 = "https://medication.med-united.health/ajax/search/drugs/auto/?query=" + medicationToLookup + "-" + formToLookup
	print(query1)
	x1 = requests.get(query1)

	queryResult1 = json.loads(x1.text)

	if (len(queryResult1["results"]) == 0): # no results found

		query2 = "https://medication.med-united.health/ajax/search/drugs/auto/?query=" + medicationToLookup
		print(query2)
		x2 = requests.get(query2)

		queryResult2 = json.loads(x2.text)
		
		if (len(queryResult2["results"]) == 0): # no results found

			medicationToLookupInParts = re.split(r'(\d+)', medicationToLookup)
			newMedicationToLookup = '-'.join(medicationToLookupInParts)
			query3 = "https://medication.med-united.health/ajax/search/drugs/auto/?query=" + newMedicationToLookup + "-" + formToLookup
			print(query3)
			x3 = requests.get(query3)

			queryResult3 = json.loads(x3.text)
			
			if (len(queryResult3["results"]) == 0): # no results found

				query4 = "https://medication.med-united.health/ajax/search/drugs/auto/?query=" + newMedicationToLookup
				print(query4)
				x4 = requests.get(query4)

				queryResult4 = json.loads(x4.text)
				
				if (len(queryResult4["results"]) == 0): # no results found
					return ""

				else:
					print("Name found: " + queryResult4["results"][0]["name"])
					print("PZN found: " + queryResult4["results"][0]["pzn"])
					return queryResult4["results"][0]["pzn"]
			else:
				print("Name found: " + queryResult3["results"][0]["name"])
				print("PZN found: " + queryResult3["results"][0]["pzn"])
				return queryResult3["results"][0]["pzn"]
		else:
			print("Name found: " + queryResult2["results"][0]["name"])
			print("PZN found: " + queryResult2["results"][0]["pzn"])
			return queryResult2["results"][0]["pzn"]
	else:
		print("Name found: " + queryResult1["results"][0]["name"])
		print("PZN found: " + queryResult1["results"][0]["pzn"])
		return queryResult1["results"][0]["pzn"]

def getPatientInfo(text):

	patientLastName = text.split("\n")[1].split(",")[0].strip()
	patientFirstName = text.split("\n")[1].split(",")[1].strip()
	patientBirthDate_wrongFormat = text.split("\n")[2]
	patientBirthDate_day = patientBirthDate_wrongFormat.split(".")[0]
	patientBirthDate_month = patientBirthDate_wrongFormat.split(".")[1]
	patientBirthDate_year = patientBirthDate_wrongFormat.split(".")[2]
	patientBirthDate_fhirFormat = patientBirthDate_year + "-" + patientBirthDate_month + "-" + patientBirthDate_day

	return patientFirstName, patientLastName, patientBirthDate_fhirFormat


if __name__ == '__main__':

	# Medication statements PDFs in the same folder as this script
	listOfPDFsInFolder = glob.glob("*.pdf")
	print(listOfPDFsInFolder)

	allPDFsAsOneSingleDataframe_list = []

	for j in range(0, len(listOfPDFsInFolder)):
		allPagesAsOneSingleDataframe_list = []
		reader = PdfReader(listOfPDFsInFolder[j])
		text = ""
		for i in range(0, len(reader.pages)):
			print("\n --> STARTING TO PROCESS MEDICATION PLAN PDF PAGE", i+1, "OUT OF", len(reader.pages), "\n")
			page = reader.pages[i]
			text += page.extract_text() + "\n"
			if(i == 0):
				text = re.sub("((.|\n)*)Medikation", "", text)

				patientFirstName, patientLastName, patientBirthDate_fhirFormat = getPatientInfo(text)

				print("Patient", patientFirstName, patientLastName)
				print(patientBirthDate_fhirFormat)

			df = tabula.read_pdf(listOfPDFsInFolder[j], pages='all', encoding='utf-8')[i]

			df = pd.DataFrame(df.values[1:], columns=df.iloc[0])

			df = df.rename(columns={'Medikament': 'MedicationName', 'Arzt': 'PractitionerFamilyName', 'Bemerkung': 'MedicationNote', 'form': 'MedicationForm'})

			numberOfLines = df.shape[0]

			df = df.assign(PatientGivenName=([patientFirstName] * numberOfLines))
			df = df.assign(PatientFamilyName=([patientLastName] * numberOfLines))
			df = df.assign(PatientBirthdate=([patientBirthDate_fhirFormat] * numberOfLines))
			df = df.assign(PharmacyName=(['??PharmacyUnknown??'] * numberOfLines))

			# Create empty columns for fields required by CSV importer that are cannot be found on the PDF
			df = df.assign(MedicationAmount=([''] * numberOfLines))
			df = df.assign(MedicationPZN=([''] * numberOfLines))
			df = df.assign(MedicationSize=([''] * numberOfLines))
			df = df.assign(PractitionerGivenName=([''] * numberOfLines))
			df = df.assign(PractitionerAddress=([''] * numberOfLines))
			df = df.assign(PractitionerPostalCode=([''] * numberOfLines))
			df = df.assign(PractitionerCity=([''] * numberOfLines))
			df = df.assign(PractitionerEmail=([''] * numberOfLines))
			df = df.assign(PractitionerPhone=([''] * numberOfLines))
			df = df.assign(PractitionerLANR=([''] * numberOfLines))
			df = df.assign(PharmacyAddress=([''] * numberOfLines))
			df = df.assign(PharmacyPostalCode=([''] * numberOfLines))
			df = df.assign(PharmacyCity=([''] * numberOfLines))
			df = df.assign(PharmacyPhone=([''] * numberOfLines))
			df = df.assign(PharmacyEmail=([''] * numberOfLines))

			df = df[df.MedicationName.notnull()]

			listOfMedicationDosages = []
			for index, row in df.iterrows():
				row["MedicationNote"] = str(row["MedicationNote"]).replace("\r", " ")
				row["MedicationNote"] = str(row["MedicationNote"]).replace(";", "///")
				if (str(row["MedicationNote"]) == "nan"): # prevents that a medication note with "nan" in the middle of the text gets replaced
					row["MedicationNote"] = str(row["MedicationNote"]).replace("nan", "")
				row["Wirkstoffe"] = str(row["Wirkstoffe"]).replace("\r", " ")
				if (str(row["Wirkstoffe"]) == "nan"): # prevents that a medication note with "nan" in the middle of the text gets replaced
					row["Wirkstoffe"] = str(row["Wirkstoffe"]).replace("nan", "")
				row["PractitionerFamilyName"] = str(row["PractitionerFamilyName"]).title()
				row["MedicationName"] = str(row["MedicationName"]).replace("\r", " ")
				row["MedicationForm"] = str(row["MedicationForm"]).replace("\r", " ")
				row["MedicationPZN"] = getMedicationPZN(row["MedicationName"], row["Wirkstoffe"], row["MedicationForm"])
				medicationDosage = str(row['morg.']) + '-' + str(row['mittags']) + '-' + str(row['abends']) + '-' + str(row['nachts'])
				medicationDosage = medicationDosage.replace("nan", "0")
				listOfMedicationDosages.append(medicationDosage)

			df = df.assign(MedicationDosage=listOfMedicationDosages)

			df = df.drop('morg.', axis=1)
			df = df.drop('vorm.', axis=1)
			df = df.drop('mittags', axis=1)
			df = df.drop('nachm.', axis=1)
			df = df.drop('abends', axis=1)
			df = df.drop('nachts', axis=1)
			df = df.drop('Bedarf', axis=1)
			df = df.drop('medik.', axis=1)
			df = df.drop('Individuell', axis=1)
			df = df.drop('bis', axis=1)

			allPagesAsOneSingleDataframe_list.append(df)

			allPagesAsOneSingleDataframe = pd.concat(allPagesAsOneSingleDataframe_list, ignore_index=True)

		print("\nAll medications of patient", patientFirstName, patientLastName, ":")
		print(allPagesAsOneSingleDataframe)
		nameForCSVFile = listOfPDFsInFolder[j].replace(".pdf", ".csv")
		allPagesAsOneSingleDataframe.to_csv(nameForCSVFile, encoding="utf-8")
		allPDFsAsOneSingleDataframe_list.append(allPagesAsOneSingleDataframe)

		print("*************************************************************")
		print("\t PROCESSED", j+1, "OUT OF", len(listOfPDFsInFolder), "MEDICATION STATEMENTS")
		print("*************************************************************")

	print("Medications of all patients:")
	allPDFsAsOneSingleDataframe = pd.concat(allPDFsAsOneSingleDataframe_list, ignore_index=True)
	print(allPDFsAsOneSingleDataframe)
	allPDFsAsOneSingleDataframe.to_csv("all-data.csv", encoding="utf-8")
	
