# Create your views here.
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import UserRegistrationForm, LoginForm
from .tokens import account_activation_token


def activate(request, uid_b64, token):
    user_model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uid_b64))
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login to your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid! Please request a new activation link.")
    return redirect('register')


def send_email(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_account_activation.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email {to_email} inbox and click on \
                received activation link to confirm and complete the registration')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


@login_not_required
def landing_page(request):
    return render(request, 'user_registration/landing_page.html')


@login_not_required
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_email(request, user, form.cleaned_data.get('email'))
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'user_registration/register.html', {'form': form})


@login_required
def logout_user(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login first...")
        return redirect('login')
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")


@login_not_required
def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Please confirm your email to activate your account.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, 'user_registration/login.html', {'form': form})


@login_required
def dashboard(request):
    # Add any necessary context data here
    context = {
        'recommended_destinations': [
            {'name': 'Paris', 'description': 'City of Love', 'image_url': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/2c/07/a8/2c/caption.jpg?w=1400&h=1400&s=1'},
            {'name': 'Tokyo', 'description': 'Modern meets Traditional', 'image_url': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1b/4b/5d/10/caption.jpg?w=1400&h=1400&s=1&cx=1005&cy=690&chk=v1_2ed86f729380ea073850'},
            {'name': 'New York', 'description': 'The Big Apple', 'image_url': 'https://i.natgeofe.com/k/5b396b5e-59e7-43a6-9448-708125549aa1/new-york-statue-of-liberty.jpg'},
        ]
    }
    return render(request, 'user_registration/dashboard.html', context)
