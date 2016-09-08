from django import forms
from django.forms import HiddenInput
from rango.models import Page, Category

class CategoryForm(forms.ModelForm):
	name = forms.CharField(max_length=128,
						help_text="Please enter the category name.")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	slug = forms.CharField(widget=forms.HiddenInput(), required=False)

	#An inline class to provide additional info on the form
	class Meta:
		# Provide an association between ModelForm and model
		model = Category
		fields = ('name',)

class PageForm(forms.ModelForm):
	title = forms.CharField(max_length=128,help_text="Please enter the title of the page.")
	url = forms.URLField(max_length=200,help_text="Please enter the URL of the page.")
	views = forms.IntegerField(widget=HiddenInput(), initial=0)

	class Meta:
		# Provide an association between ModelForm and model
		model = Page
		# What fields do we want to include in our form?
		# This way we don't need every field in the model present.
		# Some fields may allow NULL values, so we may not want to include them.
		# Here, we are hiding the foreign key.
		# we can either exclude the category field from the form,
		exclude = ('category',)
		# or specify the fields to include (i.e. not include the category field)
		#fields = ('title', 'url', 'views')
	# Here we override the clean() method.
	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')

		# If url is not empty and doesn't start with http://',
		# then prepend http://
		if url and not url.startswith('http://'):
			url = 'http://' + url
			cleaned_data['url'] = url
		# Always end clean() method by returning reference to the
		# cleaned_data dict. Otherwise the changes won't apply!!
			return cleaned_data
