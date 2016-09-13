from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from rango.models import Category,Page, UserProfile
from rango.forms import CategoryForm,PageForm, UserForm, UserProfileForm
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
	print (request.method)
	print (request.user)
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

@login_required
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

@login_required
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

def register(request):
	# A boolean value for telling the template
	# whether the registration is successful.
	# Set to False initially. Code changes value to
	# True when registration succeeds.
	registered = False

	# If the request is POST, we will process form data.
	if request.method == 'POST':
		# Attempt to grab info from raw form info.
		# Note that we make use of both UserForm and UserProfileForm.

		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the 2 forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save user form data to DB.
			user = user_form.save()

			# Now we has the password with the set_password method.
			# Once hashed we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves,
			# we set commit=False. This delays saving the model
			# until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			'''
			Did the user provide a profile picture? If so,
			we need to get it from input form and put it
			in the UserProfile model.
			'''
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			# Now we save the UserProfile model instance.
			profile.save()

			# Update our variable to indicate that the template
			# registration was successful.
			registered = True
		else:
			# Invalid form or forms
			print user_form.errors, profile_form.errors
	else:
		# Not POST so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user i/p.
		user_form = UserForm()
		profile_form = UserProfileForm()

	#Render the template depending on the context.
	return render(request, 'rango/register.html',
		{'user_form': user_form,
		'profile_form': profile_form,
		'registered':registered})

def user_login(request):
	# If the request is POST, try to pull out the relevant info.
	if request.method == 'POST':
		'''
		Gather username and password provided by the user.
		This is the info obtained from the form.
		We use request.POST.get('<var>') as opposed to
		request.POST['<var>'] to avoid KeyError exception.
		'''
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Use Django's machinery to attempt to see if the username/password
		# combo is valid - a User obj is returned if yes.
		user = authenticate(username=username, password=password)

		'''
		If we have a User object, the details are correct.
		If None, no user with matching credentials exist.
		'''
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We will send the user back to homepage.
				login(request, user)
				# Reverse URL mapping
				return HttpResponseRedirect(reverse('index'))
			else:
				# An inactive account was used - no logging in!
				return HttpResponse("Your Rango account is disabled!")
		else:
			# Bad login details were provided.
			print ("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")
	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a GET.
	else:
		# No context variables to pass to template system.
		return render(request, 'rango/login.html', {})

# Use the login_required() decorator to ensure only those
# logged in can access the view.
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just
	# log them out.
	print ("Inside logout")
	logout(request)
	# Take the user back to homepage.
	return HttpResponseRedirect(reverse('index'))