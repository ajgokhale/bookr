$(document).ready(function() {
    console.log("contentscript.js loaded");
    console.log("Injecting UI...");
    var checkExist = setInterval(function() {
       if ($('#tabEventDetails').length) {
          $("#tabEventDetails > div:nth-child(1)").after('<button onclick="book_room()">Book Haas Room</button>');
          clearInterval(checkExist);
       }
    }, 100);
});

function book_room() { 
    var start_time = $("#xStTiIn").val(); 
    var end_time = $("#xEnTiIn").val(); 
    var date = $("#xStDaIn").val();
    alert(start_time + end_time);
} 