from django import forms


class FirstStepForm(forms.Form):
    numVar = forms.IntegerField(label = 'Número de variáveis')
    numRest = forms.IntegerField(label = 'Número de restrições')
    sucess_url = "/second-step"
        

class SecondStepForm(forms.Form):
    #restri = forms.CharField(label = 'Restrições', widget=forms.TextInput(attrs={'size': '40'}))
    def __init__(self, n,  *args, **kwargs):
        super(SecondStepForm, self).__init__(*args, **kwargs)
        for i in range(0, n):
            self.fields["restricao %d" % i] = forms.CharField()
