from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
def index(request):
	return HttpResponse("Hi there!!<br><a href='/rango/about'>About Page</a>")
	#return render(request, 'rango/index.html')

def about(request):
	return HttpResponse("Hi there from About page...<br><a href='/rango/'>Index</a>")
	#return render(request, 'rango/about.html')
