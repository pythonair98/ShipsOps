
window.addEventListener("load", () => {
  function sendData() {
    const myRequest = new XMLHttpRequest();

    const FD = new FormData(form);

    myRequest.addEventListener("load", (event) => {
      console.log(event.target.responseText);
    });

    myRequest.addEventListener("error", (event) => {
      alert("Oops! Something went wrong.");
    });

    myRequest.open("POST", "contracts",false);

    myRequest.send(FD);

    location.reload();


  }
  const form = document.getElementById("my-form");
  form.addEventListener("submit", (event) => {
    event.preventDefault();

    sendData();
  });
});
