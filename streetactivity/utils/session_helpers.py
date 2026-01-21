from django.urls import reverse

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
