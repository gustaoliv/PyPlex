import pdb

from django import forms


class FirstStepForm(forms.Form):
    METHOD_CHOICES = [('PRIMAL', 'Primal'),
                      ('DUAL', 'Dual')]
    EXIBITION_TYPE_CHOICES = [('GRAFICA', 'Gráfica'),
                              ('TABULAR', 'Tabular')]

    exibition_type = forms.ChoiceField(choices=EXIBITION_TYPE_CHOICES, widget=forms.RadioSelect, label='Tipo')
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect, label='Método')
    numVar = forms.IntegerField(label='Número de variáveis')
    numRest = forms.IntegerField(label='Número de restrições')
    integer_solution = forms.BooleanField(label="Utilizar solução inteira", required=False)
    sucess_url = '/second-step'


class SecondStepForm(forms.Form):
    def __init__(self, numVar, numRest, *args, **kwargs):
        super(SecondStepForm, self).__init__(*args, **kwargs)

        # objetive function
        OBJECTIVE_CHOICES = [('MAXIMIZE', 'MAXIMIZE'), ('MINIMIZE', 'MINIMIZE')]
        self.fields['objective'] = forms.ChoiceField(choices=OBJECTIVE_CHOICES, label='objective')

        for i in range(numVar):
            self.fields[f'x{i}'] = forms.IntegerField(initial=0, label=f'x{i + 1}')

        # restrictions
        for i in range(numRest):
            for j in range(numVar + 2):
                if j == numVar:
                    choices = [('<=', '<='), ('=', '='), ('>=', '>=')]
                    self.fields[f'a{i}{j}'] = forms.ChoiceField(choices=choices, label='signal')
                elif j < numVar:
                    self.fields[f'a{i}{j}'] = forms.IntegerField(initial=0, label=f'x{j + 1}')
                else:
                    self.fields[f'a{i}{j}'] = forms.IntegerField(initial=0, label=f'dontShow')
