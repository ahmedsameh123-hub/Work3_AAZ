  const form = document.getElementById('form');
  const errorMessage = document.getElementById('errorMessage');

  const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;

  form.addEventListener('submit', (e) => {
      const localEmail = document.getElementById('txtEmail').value;

      let messages = []

      if (localEmail.length == 0) {
          messages.push('Oops! Please add your email')
      } else {
          if (localEmail.match(emailPattern)) {} else {
              messages.push('Oops! Please check your email')
          }
      }

      if (messages.length > 0) {
          e.preventDefault()
          errorMessage.innerText = messages.join(', ')
      }

  })