from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import detect_user, send_verification_email
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Restrict vendor from accessing customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict customer from accessing vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name, last_name, username, email, phone_number, password
            )
            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = "Activate Your User Account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(
                request, user, mail_subject, email_template
            )

            messages.success(
                request, "Your account has been created successfully!"
            )

            return redirect("myAccount")
        else:
            print("invalid form")
            print(form.errors)
            # pass
    else:
        form = UserForm()

    context = {
        "form": form,
    }

    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid:
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name, last_name, username, email, phone_number, password
            )
            user.role = User.VENDOR
            user.save()

            # Send verification email
            mail_subject = "Activate Your Vendor Account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(
                request, user, mail_subject, email_template
            )

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(
                request,
                "Your account has been registered successfully! Please wait for approval.",
            )
            return redirect("myAccount")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
        vendor_form = VendorForm()

    context = {
        "form": form,
        "vendor_form": vendor_form,
    }

    return render(request, "accounts/registerVendor.html", context)


def activate(request, uidb64, token):
    # Activate user by setting is_active to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Congratulations! Your account has been activated"
        )
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("myAccount")


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect("myAccount")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")
    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out")
    return redirect("login")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset password email
            mail_subject = "Reset Your Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(
                request, user, mail_subject, email_template
            )

            messages.success(
                request,
                "Password reset link has been sent to your email address",
            )
            return redirect("login")
        else:
            messages.error(
                request,
                "Account does not exist",
            )
            return redirect("forgotPassword")

    return render(request, "accounts/forgotPassword.html")


def resetPasswordValidate(request, uidb64, token):
    # Validate user by decoding the token
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has expired")
        return redirect("myAccount")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
            return redirect("resetPassword")
    return render(request, "accounts/resetPassword.html")


@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectUrl = detect_user(user)
    return redirect(redirectUrl)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")
