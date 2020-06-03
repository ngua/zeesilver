const resendButton = document.querySelector('#resend');
const messages = document.querySelector('#messages');
resendButton.addEventListener('click', (e) => {
  e.preventDefault();
  fetch(resendButton.href, {
    'method': 'GET'
  })
    .then(response => response.json())
    .then(data => {
      const message = document.createElement('div');
      message.classList.add('alert', 'alert-success');
      message.innerText = data.message;
      messages.appendChild(message);
    })
    .catch(error => {console.log(`Error: ${error}`)})
})
