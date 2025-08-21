const sodium = require('libsodium-wrappers');

async function encryptMessage(message, key) {
  await sodium.ready;
  const nonce = sodium.randombytes_buf(sodium.crypto_secretbox_NONCEBYTES);
  const encrypted = sodium.crypto_secretbox_easy(sodium.from_string(message), nonce, key);
  return { encrypted, nonce };
}

module.exports = { encryptMessage };

if (typeof window !== 'undefined') {
  window.encryptMessage = encryptMessage;

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const messageField = document.querySelector('#id_body');
    const keyBase64 = window.keyBase64; // Set this in your template

    if (!form || !messageField || !keyBase64) return;

    sodium.ready.then(() => {
      const key = sodium.from_base64(keyBase64);
      form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const { encrypted, nonce } = await encryptMessage(messageField.value, key);
        messageField.value = btoa(String.fromCharCode(...encrypted));
        let nonceInput = form.querySelector('input[name="nonce"]');
        if (!nonceInput) {
          nonceInput = document.createElement('input');
          nonceInput.type = 'hidden';
          nonceInput.name = 'nonce';
          form.appendChild(nonceInput);
        }
        nonceInput.value = btoa(String.fromCharCode(...nonce));
        form.submit();
      });
    });
  });
}

module.exports = { encryptMessage };