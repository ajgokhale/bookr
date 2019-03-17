var state = "ready-to-book";
var start_saved;
var end_saved;
var date_saved;
var token = null;

function book_room() { 

    var start_time = $("#xStTiIn").val(); 
    var end_time = $("#xEnTiIn").val(); 
    var date = $("#xStDaIn").val();
    if (state == "ready-to-book") {
        alert("Booking a room from " + start_time + " to " + end_time + " on " + date);
        request_available_rooms(start_time, end_time, date);

        state = "choose-room";

    } else if (state == "choose-room") {
        if (start_time != start_saved || 
            end_time != end_saved ||
            date != date_saved) {

            state = "ready-to-book";
            book_room();
            
        } else {
            var selected_room = $('#select_room').find(":selected").text();
            //var room_code = $('#select_room').find(":selected").getAttribute("value");
            var room_code = "dummy";
            alert("Booking " + selected_room);

            var event_id = request_room(room_code);

            var add = document.getElementById("xDescIn")
            add.removeChild(add.firstChild);

            $('#hInySc0').append("Event ID: " + event_id + '<br>' );

            state = "booked";
        }
    }
    
} 

function remove_button() {
    $("#book_room").attr("hidden",true);
    $("#account").text("Login");
    document.getElementById('account').onclick = get_login_token;
}

function logout() {
    token = null;
    chrome.storage.local.set({t: "na"}, function(result){
      console.log("The token has been unset");
      remove_button();
    });
}
/*
chrome.storage.onChanged.addListener(function(changes, namespace) {
        for (var key in changes) {
          var storageChange = changes[key];
          if (namespace == "")
          console.log('Storage key "%s" in namespace "%s" changed. ' +
                      'Old value was "%s", new value is "%s".',
                      key,
                      namespace,
                      storageChange.oldValue,
                      storageChange.newValue);
        }
      });
*/

function insert_button() {
    console.log("Injecting UI...");

    var checkExist = setInterval(function() {
       if ($('#tabEventDetails').length) {
        $("#account").text("Logout");
        document.getElementById('account').onclick = logout;
          $("#tabEventDetails > div:nth-child(1)").after(
            '<button id="book_room" onclick="book_room()" class="btn-small btn-meeting">Book Haas Room</button>');
          clearInterval(checkExist);
          document.getElementById('book_room').onclick = book_room;
       }
    }, 100);
}

function get_login_token() {
    chrome.storage.local.get({t: "na"}, function(result) {
        if (result.t == "na" || result.t == token) {
            chrome.runtime.sendMessage({request: "login"}, function(response) {
                if (response.success != "success") {
                    alert("Log in failed");
                } else {
                    token = response.t;
                    insert_button();
                }
            });
        }
        else {
            token = result.t;
            insert_button();
        }
    });
    
}


$(document).ready(function() {
    console.log("contentscript.js loaded");

    console.log("Authenticating user");
    var checkExist = setInterval(function() {
       if ($('#tabEventDetails').length) {
        $("#tabEventDetails > div:nth-child(1)").after(
            '<button id="account" onclick="get_login_token()" class="btn-small btn-meeting">Login</button>');
          clearInterval(checkExist);
          document.getElementById('account').onclick = get_login_token;
       }
    }, 100);
    get_login_token();
});

function event_info_updated() {

}



function request_available_rooms(start_time, end_time, date) {

// Send request for available rooms, given event details as arguments
// Request should be sorted in descending order of room capacity
    // Use default value for now
    const capacity = "2";

    var Url = 'http://localhost:8080/request-room/';
    alert("sending request");
    $.ajax({
        url: Url,
        type: "POST",
        data: {st: start_time, et: end_time,
            dt: date, cpty: capacity, t: token},
        datatype: 'json',
        success: function(response){
            if (response == "logged-out") {
                get_login_token();
            } else if (response == "not-enough-info") {
                alert("There was a system error, please try again in a few seconds.");
            } else if (response == "no-rooms-available") {
                alert("There are no rooms available at the time you've selected. Please try another time.");
            } else {
                present_rooms(response);
            }
            
        },
        error:function(error){
            alert('error');
        }
    });

    // document.getElementById("book_room").outerHTML = "";
    // $("#tabEventDetails > div:nth-child(1)").after('<button id="book_room" onclick="book_room()" class="btn-small btn-meeting">Book Haas Room</button>');
    
}

function present_rooms(response) {
    var rooms = response.split(", ");
    const length = rooms.length;
    var element = '<select id="select_room" class="btn-small btn-meeting">';
    for (var i = 0; i < length; i+=2) {
        element = element.concat('<option>');
        element = element.concat( rooms[i] + ' ' + rooms[i + 1] );
        element = element.concat('</option>');
    }
    element =element.concat( '</select>' );
    if ($('#tabEventDetails').length) {
        $("#tabEventDetails > div:nth-child(1)").after(element);
    }
}

function request_room(selected_room) {

// Send request to book room, given the room code as an argument
// The room summarizes both the time and location of the event being booked
// It can be passed as a token to the server

// The function will return the event's unique code that will be saved in the event's description
    return "8ref94hf";
}