// if Result is empty, hide it
/*
const btn = document.querySelector(".calculate");

function greet(event) {
  console.log("greet:", event);
}

function displayResult(event) {
  const outpt = document.querySelector(".result output");
  outpt.
}

btn.onclick = displayResult;

outpt.onchange;
*/
/*
window.addEventListener("DOMContentLoaded", (event) => {
  console.log("DOM fully loaded and parsed");
});
*/
//$("#myForm").ajaxForm({
// url: "solargeometry.igwegbu.tech/", // or whatever
//dataType: "json",
// success: function (response) {
//   alert("The server sent a response"); //says: " + response);
// },
//});

//var xhr = new XMLHttpRequest();
//xhr.open("POST", "http://127.0.0.1:5000");
//xhr.onload = function (event) {
// alert("Success, server responded"); // with: " + event.target.response); // raw response
//};
// or onerror, onabort
//var formData = new FormData(document.getElementById("myForm"));
//xhr.send(formData);
//

//const btn = document.querySelector("button");
/*
function random(number) {
  return Math.floor(Math.random() * (number + 1));
}*/
/*
btn.addEventListener("click", () => {
  alert("Hello");
  console.log("Hello");
  //document.querySelector("#result").setAttribute("hidden", "False");
});*/
function checkResult() {
  geoResultText = document.getElementById("geoResultText");
  geoOutput = document.getElementById("geoOutput");

  if (geoOutput.innerText.startsWith("#")) {
    geoResultText.innerHTML = "The solar panel is fully shaded.";
  }
  //document.getElementById("result").getAttribute("name");
}
