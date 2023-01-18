
document.querySelector("#signin-form").classList.add("hidden");
document.querySelector("#signin-btn").addEventListener('click', function() {
  document.querySelector("#signin-form").classList.remove("hidden");
});


document.querySelector("#signin-form .fa-times").addEventListener('click', function() {
  document.querySelector("#signin-form").classList.add("hidden");
});




document.querySelector("#register-form").classList.add("hidden");
document.querySelector("#register-btn").addEventListener('click', function() {
  document.querySelector("#register-form").classList.remove("hidden");
});


document.querySelector("#register-form .fa-times").addEventListener('click', function() {
  document.querySelector("#register-form").classList.add("hidden");
});
