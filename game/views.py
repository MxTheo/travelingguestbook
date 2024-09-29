from usermanagement.models import Profile

# Create your views here.
def calc_percentage_xp(user):
    '''Given the user, calculate the percentage the user acquired for xp,
    so that it can be used in the progress bar
    '''
    profile           = Profile.objects.get(user=user)
    start_xp = profile.xp - profile.xp_start_lvl
    end_xp = profile.xp_next_lvl - profile.xp_start_lvl
    percentage = start_xp/end_xp*100
    return round(percentage)

