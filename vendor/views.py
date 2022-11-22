from django.shortcuts import render
from .forms import VendorForm
from accounts.forms import UserProfileForm

# Create your views here.
def vendor_profile(request):
    profile_form = UserProfileForm()
    vendor_form = VendorForm()

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
    }
    return render(request, "vendor/vendor_profile.html", context)
