import base64
import nacl.secret
from django.db import models
from django.urls import reverse


class ChatRoom(models.Model):
    """The object that is passed from person to person"""

    slug         = models.SlugField(
        verbose_name="Code om de chatroom te kunnen vinden",
        max_length=10,
        unique=True,
        editable=False,
    )
    secret_key = models.CharField(
        max_length=44, editable=False)
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Datum aangemaakt"
    )

    class Meta:
        """Order descending"""

        ordering = ["-date_created"]

    def get_absolute_url(self):
        """Given the slug of the chatroom,
        returns the url with the slug appended after,
        so that chatroompage is findable by the reciever of the chatroom"""
        return reverse("chatroom", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.slug)


class ChatMessage(models.Model):
    """The message the receiver of the chatroom leaves on the chatroom page"""

    chatroom  = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    name      = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Je (voor)naam",
        help_text="Een naam geeft al context. Niet verplicht. Anoniem kan ook",
    )
    body      = models.TextField(
        max_length=3000,
        verbose_name="Bericht",
        help_text="Schrijf hier je bericht. Maximaal 3000 karakters",
        default="Hallo"
    )
    nonce = models.CharField(max_length=64)
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Datum aangemaakt"
    )
    date_changed = models.DateTimeField(verbose_name="Datum bewerkt", null=True)

    class Meta:
        """Order chatmessages in descending order by date created"""
        ordering = ["-date_created"]

    def __str__(self):
        return str(self.body[0:50] + " . . .")

    def get_decrypt_key(self):
        '''Get the key from the associated ChatRoom, base64-decode'''
        key_b64 = self.chatroom.secret_key
        key = base64.b64decode(key_b64)
        return key

    def get_absolute_url(self):
        """After entering a message,
        the visitor is redirected towards the chatroom detail page"""
        return reverse("chatroom", kwargs={"slug": self.chatroom.slug})

    @property
    def decrypted_body(self):
        """Decrypt the body of the message using the secret key and nonce"""
        try:
            key = self.get_decrypt_key()
            box = nacl.secret.SecretBox(key)
            nonce = base64.b64decode(self.nonce)
            encrypted = base64.b64decode(self.body)
            decrypted = box.decrypt(encrypted, nonce)
            return decrypted.decode('utf-8')
        except Exception as e:
            return "[Fout bij decryptie]"+str(e)
