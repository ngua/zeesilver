const cardButton = document.querySelector('#sq-creditcard');
const applicationId = JSON.parse(document.querySelector('#square-application-id').textContent);
const paymentUrl = JSON.parse(document.querySelector('#payment-url').textContent);
const csrf = Cookies.get('csrftoken');

const paymentForm = new SqPaymentForm({
  applicationId: applicationId,
  inputClass: 'sq-input',
  autoBuild: false,
  inputStyles: [{
    fontSize: '16px',
    lineHeight: '24px',
    padding: '16px',
    placeholderColor: '#a0a0a0',
    backgroundColor: 'transparent',
  }],
  cardNumber: {
    elementId: 'sq-card-number',
    placeholder: 'Card Number'
  },
  cvv: {
    elementId: 'sq-cvv',
    placeholder: 'CVV'
  },
  expirationDate: {
    elementId: 'sq-expiration-date',
    placeholder: 'MM/YY'
  },
  postalCode: {
    elementId: 'sq-postal-code',
    placeholder: 'Postal'
  },
  callbacks: {
    cardNonceResponseReceived: function (errors, nonce, cardNumber) {
      if (errors) {
        return;
      }
      console.log(nonce);
      sendNonce(nonce);
    }
  }
});

document.addEventListener('DOMContentLoaded', () => {
  paymentForm.build();
})

cardButton.addEventListener('click', (e) => {
  e.preventDefault();
  paymentForm.requestCardNonce();
});

function sendNonce(nonce) {
  fetch(paymentUrl, {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf,
      'credentials': 'include',
      'X-Requested-With': 'XMLHttpRequest'
    }),
    body: JSON.stringify({nonce: nonce})
  })
    .then(response => response.json())
    .then(data => {
      const url = data.url;
      window.location.replace(url);
    })
    .catch(error => {console.log(`Error: ${error}`)})
}
