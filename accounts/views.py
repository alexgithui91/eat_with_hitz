from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User

# Create your views here.
def registerUser(request):
    if request.method == "POST":
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            # Create user using form
            # password = form.cleaned_data["password"]
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # # Create the user using create_user method
            # "username",
            # "email",
            # "phone_number",
            # "password",
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
            print("I have created ze user")

            return redirect("registerUser")
    else:
        form = UserForm()

    context = {
        "form": form,
    }

    return render(request, "accounts/registerUser.html", context)
