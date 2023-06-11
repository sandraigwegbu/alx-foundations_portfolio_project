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

//const { getEventListeners } = require("events");

//var xhr = new XMLHttpRequest();
//xhr.open("POST", "http://127.0.0.1:5000");
//xhr.onload = function (event) {
// alert("Success, server responded"); // with: " + event.target.response); // raw response
//};
// or onerror, onabort
//var formData = new FormData(document.getElementById("myForm"));
//xhr.send(formData);
//

//const btn = document.querySelector(".calculate");
/*
function random(number) {
  return Math.floor(Math.random() * (number + 1));
}*/

//btn.addEventListener("click", () => {
//alert("Hello");
//city = document.getElementById("city");
//if (city.innerText === "Unknown city") {
// alert("Unknown city");
//}
//console.log("Hello");
//document.querySelector("#result").setAttribute("hidden", "False");
//});
/* if geoOutput is negative; set geoResultText display to none.
var btn = document.querySelector("calculate");
*/
/*
function checkResult() {
  alert("Here");
  geoResultText = document.getElementById("geoResultText");
  geoOutput = document.getElementById("geoOutput");
  alert("Here");
  alert(geoResultText.innerHTML);
  alert(geoOutput.value);
*/
function checkResult() {
  geoResultText = document.getElementById("geoResultText");
  geoOutput = document.getElementById("geoOutput");
  //dateString = document.getElementById("dateString");
  //alert(dateStrin);
  if (geoOutput.value.startsWith("-")) {
    //alert("Yes - negative");
    geoResultText.innerHTML =
      "<h3 style='color:red; margin-bottom: 0; padding-bottom:0'>The solar panel is fully shaded.</h3></br><em style='margin-top:0; padding-top:0'>(The Solar Geometry Factor is zero.)</em>";
    // geoResultText.style.display = "none";
  } else if (geoOutput.value === "") {
    geoResultText.innerHTML =
      "<em style='color: blue;'>Fill in the <span style='opacity: 100%; padding: 0.5em; border-radius: 8px; background-color: white; color: black;'>white</span> cells above and press <strong>Calculate</strong>.</em>";
  } else {
    geoResultText.style.display = "block";
  }
}

//document.getElementById("result").getAttribute("name");
//alert("You clicked me");
//Initi app on load
//const activeMenu = document.getElementById("welcome");
//alert("The active menu is " + `$(activeMenu)`);

//const landingPageButton = document.querySelector("landingPageButton");
//const landingPageButton = document.getElementById("landingPageButton");
//landingPageButton.addEventListener("click", (event) => {
//const welcomeMenu = document.getElementById("welcomeMenu");
//alert("Loading Calculator");
//alert(welcomeMenu.nodeValue);
//});

//unction loadCalculator() {
//const activeMenu = document.getElementById("welcome");
//activeMenu.setAttribute("color", "red");
//alert("Loading Calculator");
//alert(activeMenu);
// alert(activeMenu.baseURI);
//previousMenu = activeMenu;
//activeMenu = document.getElementById("calculator");
// previousMenu.setAttribute("background-color", "red");
//currentMenu.setAttribute("background-color", "blue");
//}
/*
const navMenu = document.querySelectorAll(".menu");
navMenu.forEach((menuItem) => {
  menuItem.addEventListener("click", () => {
    //alert("Menu Item Clicked");
  });
});
*/
