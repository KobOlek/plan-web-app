/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
  var plans = document.getElementsByClassName("plan");
  for (let index = 0; index < plans.length; index++) {
    plans[index].querySelector("#myDropdown").classList.toggle("show"); 
  }
}

// // Close the dropdown menu if the user clicks outside of it
// window.onclick = function(event) {
//   if (!event.target.matches('.dropbtn')) {
//     var dropdowns = document.getElementsByClassName("dropdown-content");
//     var i;
//     for (i = 0; i < dropdowns.length; i++) {
//       var openDropdown = dropdowns[i];
//       if (openDropdown.classList.contains('show')) {
//         openDropdown.classList.remove('show');
//       }
//     }
//   }
// }

let sidebar = document.getElementsByClassName("sidebar")[0]; 
function open_sidenav() {
  sidebar.style.animation = "appearing .5s";
  sidebar.style.display = "flex";
}

function animate_closing_sidenav() {
  sidebar.style.animation = "disappearing .2s";
}

sidebar.addEventListener("animationend", () => {
  if(sidebar.style.animationName == "disappearing")
    sidebar.style.display = "none";
});