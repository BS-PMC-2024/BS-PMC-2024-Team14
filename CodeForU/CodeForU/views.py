#from django.http import HttpResponse

from django.shortcuts import render


def homepage(request):
    #return HttpResponse("Hello World! I'm Home.")
    user_profile = request.user if request.user.is_authenticated else None
    return render(request,'homepage.html',{"user_profile":user_profile})



def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

