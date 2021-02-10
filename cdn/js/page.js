var css = document.getElementById("css");

if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
  css.href = "cdn/css/mobile.css";
};

window.onscroll = function() {
  scrollBar()
};
var inputs = document.getElementById("inputs");
var sticky = inputs.offsetDown;

function scrollBar() {
  if (window.pageYOffset >= sticky) {
    inputs.classList.add("sticky")
  } else {
    inputs.classList.remove("sticky");
  }
}

var items = document.getElementsByClassName("input");

function bar() {
  for (i = 0; i < items.length; i++) {
    if (items[i].style.display === "none") {
      items[i].style.display = "unset";
    } else {
      items[i].style.display = "none";
    }
  }
}
