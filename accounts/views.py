from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import TemplateView, FormView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

from .forms import RegisterForm

# Create your views here.


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save()
        generate_verification_email(user, self.request)
        return redirect("/accounts/ver-req/" + user.email + "/")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=email, password=password)
        if user:
            if user.is_verified:
                login(request, user)
                messages.success(request, "successful")
                return redirect("posts:home")
            else:
                return render(
                    request, "accounts/login.html", {"error": True, "error_msg": "please verify your email address"}
                )
        else:
            return render(
                request, "accounts/login.html", {"error": True, "error_msg": "username or password is incorrect"}
            )

    return render(request, "accounts/login.html")


def generate_verification_email(user, request):
    # token generation
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    current_site = get_current_site(request)

    subject = "FakeInsta: Verify Your Email Address"
    text_content = f"Please click the following link to verify your email address. http://{current_site}/accounts/activate/{uid}/{token}/"

    html_content = f"""
    <h1>Welcome to FakeInsta!</h1>
    <h3 style="color:gray">Verify Your Email Address</h3>
    <p>Please click the following link to verify your email address.</p>
    <a href="http://{current_site}/accounts/activate/{uid}/{token}/">
    Verify Your Email Address</a>
    """

    email = EmailMultiAlternatives(subject, text_content, to=[user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        if user.is_verified:
            return render(request, "accounts/verification_success.html", {"status": "already"})

    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        return render(request, "accounts/verification_success.html", {"status": "success"})
    else:
        return render(request, "accounts/verification_success.html", {"status": "invalid"})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def verification_required(request, email):
    return render(request, "accounts/verification_required.html", {"email": email})


def page_not_found_view(request, exception):
    return render(request, "error404.html", {})