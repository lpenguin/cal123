from django import forms


class EventForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    begin_date = forms.DateTimeField()
    end_date = forms.DateTimeField(required=False)
