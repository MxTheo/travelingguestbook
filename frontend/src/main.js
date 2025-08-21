import * as sodium from "libsodium-wrappers";

export async function encryptMessage(message, key) {
  await sodium.ready;
  const nonce = sodium.randombytes_buf(sodium.crypto_secretbox_NONCEBYTES);
  const encrypted = sodium.crypto_secretbox_easy(sodium.from_string(message), nonce, key);
  return { encrypted, nonce };
}

window.encryptMessage = encryptMessage;

async function setupEncrypt() {
  await sodium.ready;
  const form = document.querySelector('form');
  const messageField = document.querySelector('#id_body');
  const keyBase64 = window.keyBase64;
  
  if (!form || !messageField || !keyBase64) return;

  let key;
  try {
    key = sodium.from_base64(keyBase64, sodium.base64_variants.ORIGINAL);
  } catch (err) {
    console.error("Fout bij from_base64:", err);
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

document.addEventListener('DOMContentLoaded', () => {
  setupEncrypt();
});
