var upgradeTime = document.querySelector(".timer").textContent;//CHANGE ME - 2 Events in one page will only display one timer, so for now use timer only on event template page individually :)
var seconds = upgradeTime;
function timer() {
  var days        = Math.floor(seconds/24/60/60);
  var hoursLeft   = Math.floor((seconds) - (days*86400));
  var hours       = Math.floor(hoursLeft/3600);
  var minutesLeft = Math.floor((hoursLeft) - (hours*3600));
  var minutes     = Math.floor(minutesLeft/60);
  var remainingSeconds = seconds % 60;
  function pad(n) {
    return (n < 10 ? "0" + n : n);
  }
  document.querySelector(".timer").innerHTML = pad(days) + "D:" + pad(hours) + "H:" + pad(minutes) + "M:" + pad(remainingSeconds) + "S";
  if (seconds == 0) {
    clearInterval(countdownTimer);
    document.querySelector(".timer").innerHTML = "O Evento Terminou"; //CHANGE ME - Make me say "A sortear.." for 2 Seconds or 3 and then change it to "O Evento Terminou"
  } else if (seconds > 0) {
    seconds--;
  } else if (seconds < 0) {
    document.querySelector(".timer").innerHTML = "O Evento Terminou";
  }
}
timer();
var countdownTimer = setInterval('timer()', 1000);