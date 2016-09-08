from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category,Page
from rango.forms import CategoryForm,PageForm
# Create your views here.
def index(request):
	#return HttpResponse("Hi there!!<br><a href='/rango/about'>About Page</a>")
	"""
	Construct a dictionary to pass to template engine as its context.
	Note the key boldmessage is same as {{ boldmessage }} in the template!
	"""
	#context_dict = {'boldmessage': "Processing our own webpage!!",}
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the first parameter is the template we wish to use.

	#return render(request, 'rango/index.html', context = context_dict)

	'''
	Query the database for a lost of ALL categories currently stored.
	Order the categories by no. of likes in descending order.
	Retrieve top 5 only or all if less than 5.
	Place the list in our context_dict dictionary.
	This will be passed to the template engine.
	'''
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list,
					'pages': page_list,}

	#Render the response and send it back!
	return render(request, 'rango/index.html', context_dict)

def about(request):
	#return HttpResponse("Hi there from About page...<br><a href='/rango/'>Index</a>")
	context_dict = {'admin_name': "Ayan Majumdar",}
	return render(request, 'rango/about.html', context = context_dict)

def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict = {}

	try:
		# Can we find a category name slug with the given name?
		# If we can't the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an
		# exception.
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages.
		# Note taht filter() will return a list of page objects or empty
		# list.
		pages = Page.objects.filter(category = category)

		# Adds our results list to the template context under the name "pages"
		context_dict['pages'] = pages
		# We also add the category object from the database to
		# the context dict.
		# We will use this in template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we did not find the specified category.
		# Don't do anything, template will display no category message
		context_dict['pages'] = None
		context_dict['category'] = None

	# Go render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)

def add_category(request):
	form = CategoryForm()
	# A HTTP POST?
	'''
	The first time this will be called from index link, we will show the 
	blank form, for that the request will be GET, and we use the blank
	form object. It will pass that via context dictionary back to same
	URL rango/add_category/ 
	Now, we fill up form and click Submit, that will again hit this view
	but the request will be POST.
	'''
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save new category in DB
			cat = form.save(commit=True)
			print(cat, cat.slug)
			# Now that the category is saved we could give a confirmation
			# message but since the most recent category added is on index page
			# we can direct user back to index page.

			return index(request)
		else:
			# The supplied form contained errors - 
			# just print them to terminal
			print (form.errors)
	# Will handle bad form, new form, or no form supplied cases.
	# Render the form with error msg if any.
	return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
		#category = Category()
		#category.save()
	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				'''
				NB:Here we need to set some attributes of page 1st
				most importantly the category. Hence we do commit=False
				This is VITAL as True will give NULL exception. Here,
				we set the attributes and then call page.save() to commit.
				'''
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print form.errors
	context_dict = {'form':form, 'category':category}
	return render(request, 'rango/add_page.html', context_dict)
