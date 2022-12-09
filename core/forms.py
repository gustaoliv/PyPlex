import pdb
from django import forms


class FirstStepForm(forms.Form):
    METHOD_CHOICES = [('PRIMAL', 'Primal'),
                      ('DUAL', 'Dual')]
    EXIBITION_TYPE_CHOICES = [('GRAPHIC', 'Gráfica'),
                              ('TABULAR', 'Tabular')]

    exibition_type = forms.ChoiceField(choices=EXIBITION_TYPE_CHOICES,initial=EXIBITION_TYPE_CHOICES[1],
                                       widget=forms.RadioSelect(attrs={'class':'form-check-input','onchange': 'VerificaVal()', 'id':'tipo'}), label='Tipo',
                                       )
    method = forms.ChoiceField(choices=METHOD_CHOICES,initial=METHOD_CHOICES[0],
                               widget=forms.RadioSelect(attrs={'class':'form-check-input'}), label='Método')

    numVar = forms.IntegerField(label='Número de variáveis', min_value=2, 
                                widget=forms.NumberInput(attrs={'class':'form-control','id': 'val'}))
    numRest = forms.IntegerField(label='Número de restrições',min_value=1,
                                 widget=forms.NumberInput(attrs={'class':'form-control'}))
    integer_solution = forms.BooleanField(label="Utilizar solução inteira", required=False,
                                          widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    sucess_url = '/second-step'


class SecondStepForm(forms.Form):
    def __init__(self, numVar, numRest, *args, **kwargs):
        super(SecondStepForm, self).__init__(*args, **kwargs)

        # objetive function
        OBJECTIVE_CHOICES = [('MAXIMIZE', 'Maximizar'), ('MINIMIZE', 'Minimizar')]
        self.fields['objective'] = forms.ChoiceField(choices=OBJECTIVE_CHOICES, label='objective',
                                                     widget=forms.Select(attrs={'class':'form-control text-center'}))

        for i in range(numVar):
            if i != (numVar - 1):
                self.fields[f'x{i:02d}'] = forms.DecimalField(label=f'x{i + 1} + ',
                                                       widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':f'x{i + 1}'}))
            else:
                self.fields[f'x{i:02d}'] = forms.DecimalField(label=f'x{i + 1}',
                                                       widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder':f'x{i + 1}'}))

        # restrictions
        for i in range(numRest):
            for j in range(numVar + 2):
                if j == numVar:
                    choices = [('<=', '<='), ('=', '='), ('>=', '>=')]
                    self.fields[f'a{i:02d}{j:02d}'] = forms.ChoiceField(choices=choices, label='signal',
                                                                widget=forms.Select(attrs={'class':'form-control'}))
                elif j < numVar:
                    if j != (numVar - 1):
                        self.fields[f'a{i:02d}{j:02d}'] = forms.DecimalField(label=f'x{j + 1} + ',
                                                                  widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':f'x{j + 1}', 'pattern':'[0-9]+$'}))
                    else:
                        self.fields[f'a{i:02d}{j:02d}'] = forms.DecimalField(label=f'x{j + 1}',
                                                                  widget=forms.NumberInput(attrs={'class':'form-control',  'placeholder':f'x{j + 1}', 'pattern':'[0-9]+$'}))
                else:
                    if i == numRest - 1 and j == numVar + 1:
                        self.fields[f'a{i:02d}{j:02d}'] = forms.DecimalField(label=f'dontShowLast',
                                                                  widget=forms.NumberInput(attrs={'class':'form-control'}))
                    else:
                        self.fields[f'a{i:02d}{j:02d}'] = forms.DecimalField(label=f'dontShow',
                                                                     widget=forms.NumberInput(
                                                                         attrs={'class': 'form-control'}))