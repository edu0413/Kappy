var today = new Date();
var mi = today.getMinutes();
var mi = ("0" + mi).slice(-2);
var hh = today.getHours();
var hh = ("0" + hh).slice(-2);
var t = today.getTimezoneOffset();
var dd = today.getDate();
var mm = today.getMonth() + 1; //January is 0!
var yyyy = today.getFullYear();

if (dd < 10) {
   dd = '0' + dd;
}

if (mm < 10) {
   mm = '0' + mm;
} 
    
today = yyyy + '-' + mm + '-' + dd + 'T' + hh + ':' + mi;
document.getElementById("event_prompt").setAttribute("min", today);