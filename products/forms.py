from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    ModelForm for staff/superuser add and edit of products.
    Slug, created_at, and updated_at are excluded — Django manages them automatically.
    """

    class Meta:
        model = Product
        exclude = ['slug', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'original_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use friendly_name for the category dropdown when available
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].label_from_instance = (
            lambda obj: obj.friendly_name if obj.friendly_name else obj.name
        )
        # Add Bootstrap form-control class to all visible inputs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs.setdefault('class', 'form-control')
