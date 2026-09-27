from django.shortcuts import render


def home(request):
    return render(request, 'OnlyToursApp/home.html')


def register(request):
    """'Which type of user are you?' — Customer vs Tour Guide."""
    return render(request, 'OnlyToursApp/register.html')


def attractions(request):
    return render(request, 'OnlyToursApp/attractions.html')


def customerReg(request):
    return render(request, 'OnlyToursApp/customerReg.html')


def tourGuideReg(request):
    return render(request, 'OnlyToursApp/coming_soon.html', {
        'page_title': 'Tour Guide Registration',
        'message': "This is where tour guides will sign up to list their tours. Coming soon!",
    })


def book_now(request):
    return render(request, 'OnlyToursApp/book_now.html')


def tour_guide(request):
    return render(request, 'OnlyToursApp/coming_soon.html', {
        'page_title': 'Tour Guides',
        'message': "Meet our tour guides here soon.",
    })


def log_in(request):
    return render(request, 'OnlyToursApp/coming_soon.html', {
        'page_title': 'Log In',
        'message': "Account log in is coming soon.",
    })
