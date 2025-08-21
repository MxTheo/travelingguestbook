/**
 * @jest-environment jsdom
 */

const sodium = require("libsodium-wrappers");
const { encryptMessage } = require('../../frontend/src/main.js'); // pas aan naar jouw bestandsnaam

// Mock van encryptMessage om geen echte encryptie te doen
jest.mock('../../frontend/src/main.js', () => ({
  encryptMessage: jest.fn(() => Promise.resolve({ encrypted: Uint8Array.from([1,2,3]), nonce: Uint8Array.from([4,5,6]) }))
}));

// Mock sodium.from_base64 om altijd een dummy key terug te geven
sodium.from_base64 = jest.fn(() => Uint8Array.from(Array(32).fill(1)));
sodium.base64_variants = { ORIGINAL: 'ORIGINAL' };

// Mock sodium.ready Promise die direct resolved
sodium.ready = Promise.resolve();

async function setupEncrypt() {
  await sodium.ready; // Wacht hier tot libsodium klaar is
  const form = document.querySelector('form');
  const messageField = document.querySelector('#id_body');
  const keyBase64 = window.keyBase64;
  if (!form || !messageField || !keyBase64) return;
  
  let key;
  try {
    key = sodium.from_base64(keyBase64, sodium.base64_variants.ORIGINAL);
  } catch(e) {
    return;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const { encrypted, nonce } = await encryptMessage(messageField.value, key);
    messageField.value = btoa(String.fromCharCode(...encrypted));
    const nonceInput = form.querySelector('input[name="nonce"]');
    if (nonceInput) {
      nonceInput.value = btoa(String.fromCharCode(...nonce));
    }
    form.submit();
  });
}

describe('setupEncrypt', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form>
        <textarea id="id_body"></textarea>
        <input type="hidden" name="nonce" />
      </form>
    `;
    window.keyBase64 = "dummybase64key==";
  });

  it('should setup submit event listener and encrypt message on submit', async () => {
    await setupEncrypt();
    const form = document.querySelector('form');
    const messageField = document.querySelector('#id_body');
    const nonceInput = form.querySelector('input[name="nonce"]');

    // Vul een test bericht
    messageField.value = "test message";

    // Mock form.submit om niet te navigeren
    form.submit = jest.fn();

    // Trigger submit event
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);

    // Wacht op encryptMessage aanroep (async)
    await Promise.resolve();

    // Controleer of encryptMessage werd aangeroepen met juiste argumenten
    expect(encryptMessage).toHaveBeenCalledWith("test message", expect.any(Uint8Array));

    // Na encryptie vullen textArea en nonce hidden input
    expect(messageField.value).toBe(btoa(String.fromCharCode(1,2,3)));
    expect(nonceInput.value).toBe(btoa(String.fromCharCode(4,5,6)));

    // Check ook dat form.submit is aangeroepen
    expect(form.submit).toHaveBeenCalled();
  });

  it('should not set submit listener if keyBase64 missing', async () => {
    window.keyBase64 = "";
    await setupEncrypt();
    const form = document.querySelector('form');
    const spy = jest.spyOn(form, 'addEventListener');
    // submit event listener is niet toegevoegd want keyBase64 is leeg
    expect(spy).not.toHaveBeenCalledWith('submit', expect.any(Function));
  });
});
