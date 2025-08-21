/**
 * @jest-environment jsdom
 */

const sodium = require('libsodium-wrappers');

describe('Chatmessage form encryptie met inline HTML', () => {
  let form, textarea;
  let keyBase64, key;

  beforeAll(async () => {
    await sodium.ready;

    // Definieer inline HTML (geen extern bestand, dus altijd aanwezig)
    document.documentElement.innerHTML = `
      <form id="chatForm">
        <textarea name="body" id="id_body">Hallo</textarea>
        <button type="submit">Verstuur</button>
      </form>
    `;

    form = document.querySelector('form');
    textarea = document.querySelector('#id_body');

    keyBase64 = sodium.to_base64(sodium.randombytes_buf(sodium.crypto_secretbox_KEYBYTES));
    key = sodium.from_base64(keyBase64);

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const message = textarea.value;
      const nonce = sodium.randombytes_buf(sodium.crypto_secretbox_NONCEBYTES);
      const encrypted = sodium.crypto_secretbox_easy(sodium.from_string(message), nonce, key);

      textarea.value = btoa(String.fromCharCode(...encrypted));

      let nonceInput = form.querySelector('input[name="nonce"]');
      if (!nonceInput) {
        nonceInput = document.createElement('input');
        nonceInput.type = 'hidden';
        nonceInput.name = 'nonce';
        form.appendChild(nonceInput);
      }
      nonceInput.value = btoa(String.fromCharCode(...nonce));
    });
  });

  test('vervangt plaintext door versleutelde base64-tekst bij submit', () => {
    expect(form).not.toBeNull();
    expect(textarea).not.toBeNull();

    textarea.value = "Testbericht";

    const submitEvent = new Event('submit', {
      bubbles: true,
      cancelable: true
    });

    form.dispatchEvent(submitEvent);

    expect(textarea.value).not.toBe("Testbericht");
    expect(textarea.value).toMatch(/^[A-Za-z0-9+/=]+$/); // base64 check

    const nonceInput = form.querySelector('input[name="nonce"]');
    expect(nonceInput).not.toBeNull();
    expect(nonceInput.value).toMatch(/^[A-Za-z0-9+/=]+$/); // nonce base64
  });
});
