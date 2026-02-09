from django.urls import reverse
from django.shortcuts import redirect

def cancel_moment_creation(request):
    """
    Cancel the moment creation process by clearing relevant session data and
    redirecting to the appropriate cancel URL.
    
    This function should be called when a user decides to cancel adding a moment
    to an experience. It ensures that any temporary data stored in the session
    during the moment creation process is removed, and then redirects the user
    to the URL specified in the session's 'cancel_url'.
    
    Args:
        request: Django HttpRequest object containing session data

    Returns:
        HttpResponseRedirect: A redirect response to the cancel URL
    """
    clear_session_data(request)
    cancel_url = request.session.get('cancel_url', reverse('home'))
    return redirect(cancel_url)

def determine_cancel_url(view_kwargs: dict) -> str:
    """
    Determine cancel URL for AddMomentToExperience multistep flow.
    
    - If adding the first moment (no 'experience_id'), return home URL.
    - If adding subsequent moments (has 'experience_id'), return experience detail URL.
    
    Args:
        view_kwargs: kwargs from the view
    
    Returns:
        str: The determined cancel URL
    """
    if 'experience_id' in view_kwargs:
        return reverse('experience-detail', kwargs={'pk': view_kwargs['experience_id']})
    else:
        return reverse('home')

def setup_session_for_cancel(request, view_kwargs: dict) -> None:
    """
    Given a user adding a moment to an experience, set up the session
    to include a 'cancel_url' that points to the appropriate location.
    
    Args:
        request: Django HttpRequest object
        view_kwargs: kwargs from the view
    """
    # Check if we are in the AddMomentToExperience multistep flow
    if 'experience_id' in view_kwargs or reverse('add-first-moment-to-experience') in request.path:
        cancel_url = determine_cancel_url(view_kwargs)
        request.session['cancel_url'] = cancel_url

def clear_session_data(request):
    """
    Remove moment-related data from the session.
    """
    for key in [
        "cancel_url",
        "moment_data",
        "selected_activity_id",
        "experience_id",
        "from_experience",
    ]:
        if key in request.session:
            del request.session[key]