from django import forms


class AddProductForm(forms.Form):

    def __init__(self, max_limit=None, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        self.fields['quantity'] = forms.FloatField(initial=1,
                                                   min_value=0,
                                                   max_value=max_limit)

    stock_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.FloatField(initial=1,
                                min_value=0)
