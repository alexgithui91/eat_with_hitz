from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import detectUser, send_verification_email
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from django.core.exceptions import PermissionDenied

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
            # Create user using form
            # password = form.cleaned_data["password"]
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

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
            send_verification_email(request, user)

            messages.success(
                request, "Your account has been created successfully!"
            )

            return redirect("registerUser")
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
            send_verification_email(request, user)

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(
                request,
                "Your account has been registered successfully! Please wait for approval.",
            )
            return redirect("registerVendor")
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
    return


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


@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")
