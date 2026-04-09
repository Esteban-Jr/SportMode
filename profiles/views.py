from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm


@login_required
def profile(request):
    """
    Display and update the logged-in user's default delivery information.

    GET:  Render the profile page pre-filled with current saved data.
    POST: Validate and save the updated delivery fields, then re-render.

    Order history is passed via profile.orders.all() — this related
    manager will be populated once the checkout/Order model is built
    with a ForeignKey pointing back to UserProfile.
    """
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your delivery details have been updated.')
        else:
            messages.error(
                request,
                'Update failed. Please check the form and try again.'
            )
    else:
        form = UserProfileForm(instance=user_profile)

    # orders queryset — empty until the checkout app creates Orders
    # linked to this profile via a ForeignKey.
    orders = user_profile.orders.all() if hasattr(user_profile, 'orders') else []

    context = {
        'form': form,
        'orders': orders,
    }
    return render(request, 'profiles/profile.html', context)
