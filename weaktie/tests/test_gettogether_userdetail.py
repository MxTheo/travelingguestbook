"""Tests for the UserDetail view."""
from django.urls import reverse
from django.utils import timezone

from travelingguestbook.factories import WhereaboutFactory, UserFactory



class TestBasicRendering:
    """Tests for the UserDetail view."""
    def test_profile_page_renders(self, client):
        """The profile page renders for an anonymous visitor."""
        user = UserFactory()

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["profile_user"] == user


    def test_profile_page_uses_profile_user_in_context(self, client):
        """The template receives the profile owner via 'profile_user', not 'user'."""
        user = UserFactory(username="alice")

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert response.context["profile_user"] == user


    def test_username_visible_on_page(self, client):
        """The profile owner's username is rendered on the page."""
        user = UserFactory(username="alice")

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert "alice" in response.content.decode()


# ---------------------------------------------------------------------------
# Get-together grouping
# ---------------------------------------------------------------------------
class TestWhereaboutGrouping:
    """Tests for how get-togethers are grouped into next, later, and past."""
    def test_next_get_together_is_the_earliest_upcoming(self, client):
        """The next get-together is the earliest upcoming one."""
        user = UserFactory()

        later = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=10), location="Later")
        sooner = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=2), location="Eerder")
        WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=-1), location="Verleden")

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert response.context["next_get_together"] == sooner
        assert list(response.context["later_get_togethers"]) == [later]


    def test_later_get_togethers_exclude_next(self, client):
        """Later get-togethers are all upcoming ones except the next."""
        user = UserFactory()

        WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=2), location="Eerste")
        second = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=5), location="Tweede")
        third = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=9), location="Derde")

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert list(response.context["later_get_togethers"]) == [second, third]


    def test_past_get_togethers_are_ordered_newest_first(self, client):
        """Past get-togethers are ordered newest first."""
        user = UserFactory()

        older = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=-10), location="Ouder")
        newer = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=-2), location="Nieuwer")

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert list(response.context["past_get_togethers"]) == [newer, older]


    def test_no_get_togethers_returns_empty_context(self, client):
        """A user with no get-togethers has empty/None context values."""
        user = UserFactory()

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert response.context["next_get_together"] is None
        assert list(response.context["later_get_togethers"]) == []
        assert list(response.context["past_get_togethers"]) == []


    def test_get_togethers_are_scoped_to_profile_owner(self, client):
        """Get-togethers of other users are not shown on this profile."""
        owner = UserFactory(username="owner")

        WhereaboutFactory(user=owner, date=timezone.now() + timezone.timedelta(days=2), location="Van owner")
        WhereaboutFactory(date=timezone.now() + timezone.timedelta(days=2), location="Van other")

        url = reverse("user", kwargs={"username": owner.username})
        response = client.get(url)

        assert response.context["next_get_together"].location == "Van owner"
        assert all(
            gt.location != "Van other"
            for gt in response.context["later_get_togethers"]
        )
        assert all(
            gt.location != "Van other"
            for gt in response.context["past_get_togethers"]
        )


# ---------------------------------------------------------------------------
# Owner-only controls
# ---------------------------------------------------------------------------
class TestOwnerOnlyControls:
    """Tests for edit/delete controls on the profile page."""
    def test_owner_sees_edit_and_delete_buttons(self, client, auto_login_user):
        """The owner sees edit and delete links for their get-togethers."""
        client, user = auto_login_user()
        gt = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=2))

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)
        content = response.content.decode()

        assert reverse("update-get-together", kwargs={"pk": gt.pk}) in content
        assert reverse("delete-get-together", kwargs={"pk": gt.pk}) in content
        assert reverse("create-get-together") in content


    def test_anonymous_visitor_sees_no_controls(self, client):
        """An anonymous visitor sees no edit, delete or create links."""
        user = UserFactory(username="owner")
        
        gt = WhereaboutFactory(user=user, date=timezone.now() + timezone.timedelta(days=2))

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)
        content = response.content.decode()

        assert reverse("update-get-together", kwargs={"pk": gt.pk}) not in content
        assert reverse("delete-get-together", kwargs={"pk": gt.pk}) not in content
        assert reverse("create-get-together") not in content


    def test_other_logged_in_user_sees_no_controls(self, client, auto_login_user):
        """A logged-in user who is not the owner sees no controls."""
        owner = UserFactory(username="owner")
        client, _ = auto_login_user()
        gt = WhereaboutFactory(user=owner, date=timezone.now() + timezone.timedelta(days=2))


        url = reverse("user", kwargs={"username": owner.username})
        response = client.get(url)
        content = response.content.decode()

        assert reverse("update-get-together", kwargs={"pk": gt.pk}) not in content
        assert reverse("delete-get-together", kwargs={"pk": gt.pk}) not in content
        assert reverse("create-get-together") not in content


# ---------------------------------------------------------------------------
# Profile image fallback
# ---------------------------------------------------------------------------
class TestProfileImageFallback:
    """Tests for the profile image fallback behavior."""
    def test_profile_image_falls_back_to_default(self, client):
        """A user without a profile image falls back to the default image."""
        user = UserFactory()

        url = reverse("user", kwargs={"username": user.username})
        response = client.get(url)

        assert "/static/persona/images/empty_portrait.jpg" in response.content.decode()
