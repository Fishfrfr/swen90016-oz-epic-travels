from django import forms

#  Importing Hotel Inventory (CSV Upload Form)
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()