from django.urls import reverse
from travelingguestbook.factories import LogMessageFactory, SociableFactory
from sociablecreating.models import LogMessage, Sociable

class TestUpdateSociable:
    '''Test user permissions for updating the sociable'''
    def test_update_sociable_by_different_user(self, create_user, auto_login_user):
        client, _ = auto_login_user()
        owner = create_user()
        sociable = SociableFactory(owner=owner)

        sociable_changed = self.update_sociable(client, sociable, 'Hello')

        assert sociable_changed.description != 'Hello'

    def test_update_sociable_by_owner(self, auto_login_user):
        client, owner = auto_login_user()
        sociable            = SociableFactory(owner=owner)

        sociable_changed = self.update_sociable(client, sociable, 'Hello')

        assert sociable_changed.description == 'Hello'

    def update_sociable(self, client, sociable, description_to_change):
        update_sociable_url = reverse('update-sociable', args=[sociable.slug])
        client.post(update_sociable_url, data={'description': description_to_change})
        return Sociable.objects.get(slug=sociable.slug)


class TestDeleteSociable:
    def test_delete_sociable_by_different_user(self, create_user, auto_login_user):
        client, _ = auto_login_user()
        owner     = create_user()
        sociable  = SociableFactory(owner=owner)

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 1

    def test_delete_sociable_by_owner(self, auto_login_user):
        client, owner = auto_login_user()
        sociable      = SociableFactory(owner=owner)

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 0

    def test_delete_sociable_without_authentication(self, client):
        sociable = SociableFactory()

        self.delete_sociable(client, sociable)

        assert Sociable.objects.count() == 1

    def delete_sociable(self, client, sociable):
        delete_sociable_url = reverse('delete-sociable', args=[sociable.slug])
        client.delete(delete_sociable_url)

class TestDeleteLogMessage:
    def test_delete_logmessage_by_different_user(self, create_user, auto_login_user):
        client, _ = auto_login_user()
        owner     = create_user()
        sociable  = SociableFactory(owner=owner)
        logmessage  = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def test_delete_logmessage_by_owner(self, auto_login_user):
        client, owner   = auto_login_user()
        sociable        = SociableFactory(owner=owner)
        logmessage      = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 0

    def test_delete_logmessage_without_authentication(self, client):
        sociable   = SociableFactory()
        logmessage = LogMessageFactory(sociable=sociable)

        self.delete_logmessage(client, logmessage)

        assert LogMessage.objects.count() == 1

    def delete_logmessage(self, client, logmessage):
        delete_logmessage_url = reverse('delete-logmessage', args=[logmessage.id])
        client.delete(delete_logmessage_url)
