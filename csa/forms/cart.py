from django import forms


class AddProductForm(forms.Form):

    def __init__(
            self,
            max_quantity=None,
            min_quantity=None,
            quantities=None,
            *args,
            **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        initial = min_quantity or 1
        if quantities:
            choices = [
                (quantity.quantity, quantity.quantity)
                for quantity in quantities
            ]
            self.fields['quantity'] = forms.ChoiceField(choices)
        else:
            self.fields['quantity'] = forms.FloatField(
                initial=initial,
                min_value=min_quantity,
                max_value=max_quantity)

    stock_id = forms.IntegerField(widget=forms.HiddenInput())
