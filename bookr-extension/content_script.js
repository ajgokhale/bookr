var state = null;
var start_saved;
var end_saved;
var date_saved;
var token = null;

$(document).ready(function() {
    console.log("contentscript.js loaded");

    console.log("Authenticating user");
    var checkExist = setInterval(function() {
        if ($('#tabEventDetails').length) {
            $("#tabEventDetails > div:nth-child(1)").after(
                '<button id="account" onclick="get_login_token()"\
                class="uArJ5e UQuaGc Y5sE8d guz9kb M9Bg4d">Login</button>');

            $("#tabEventDetails > div:nth-child(1)").after(
                '<button id="book_room" onclick="book_room()" \
                class="uArJ5e UQuaGc Y5sE8d guz9kb M9Bg4d">Book Haas Room</button>');

            clearInterval(checkExist);
            document.getElementById('account').onclick = get_login_token;
            document.getElementById('book_room').style.visibility = "hidden";
            get_login_token();
        }
    }, 100);
});

function login_success() {
    var checkExist2 = setInterval(function() {
        if ($('#hInySc0').html()) {
            var desc = $('#hInySc0').text();
            var pos = desc.search("EventID:");
            if (pos != -1) {
                var eventId = desc.substr(pos + 9, pos + 18);
                verify_event(eventId);
            } else {
                state = "ready-to-book";
                update_interface("");
            }
            clearInterval(checkExist2);
        }
    }, 100);
}

function book_room() { 
    var start_time = $("#xStTiIn").val();
    var end_time = $("#xEnTiIn").val(); 
    var date = $("#xStDaIn").val();
    if (state == "ready-to-book") {

        alert("Booking a room from " + start_time + " to " + end_time + " on " + date);
        request_available_rooms(start_time, end_time, date);

    } else if (state == "choose-room") {
        if (start_time != start_saved || 
            end_time != end_saved ||
            date != date_saved) {

            state = "ready-to-book";
            book_room();
            
        } else {
            var selected_room = $('#select_room').find(":selected");
            alert(selected_room.text());
            var room_name = selected_room.text();

            alert("Booking " + room_name);
            var event_id = request_room(room_name);
        }
    }
    
} 

function room_booked(token) {
    var add = document.getElementById("xDescIn")
    add.removeChild(add.firstChild);

    $('#hInySc0').append("EventID: " + token + '<br>' );

    state = "booked";
    verify_event(token);
}

function logout() {
    token = null;
    chrome.storage.local.set({t: "na"}, function(result){
      console.log("The token has been unset");
      state = "logged-out";
      update_interface("");
    });
}

function update_interface(aux) {
    console.log("Injecting UI...");
    if (state == "booked") {
        $("#account").text("Logout");
        document.getElementById('account').onclick = logout;
        $("#book_room").text(aux);
        document.getElementById('book_room').style.visibility = "visible";
        document.getElementById('book_room').onclick = null;

    } else if (state == "ready-to-book") {
        $("#account").text("Logout");
        document.getElementById('account').onclick = logout;
        $("#book_room").text("Book Haas Room");
        document.getElementById('book_room').onclick = book_room;
        document.getElementById("book_room").style.visibility = "visible";  
    } else if (state == "choose-room") {
        present_rooms(aux);
    } else if (state == "logged-out") {
        document.getElementById("book_room").style.visibility = "hidden";    
        $("#account").text("Login");
        document.getElementById('account').onclick = get_login_token;
    }
}

function get_login_token() {
    chrome.storage.local.get({t: "na"}, function(result) {
        if (result.t == "na" || result.t == token) {
            chrome.runtime.sendMessage({request: "login"}, function(response) {
                if (response.success != "success") {
                    alert("Log in failed");
                } else {
                    token = response.t;
                    login_success();
                    //update_interface();
                }
            });
        }
        else {
            token = result.t;
            login_success();
            //update_interface();
        }
    });
    
}




function event_info_updated() {

}



function request_available_rooms(start_time, end_time, date) {

// Send request for available rooms, given event details as arguments
// Request should be sorted in descending order of room capacity
    // Use default value for now
    const capacity = "2";

    start_saved = start_time;
    end_saved   = end_time;
    date_saved  = date;

    var Url = 'http://127.0.0.1:8080/request-room/';
    alert("sending request");
    $.ajax({
        url: Url,
        type: "POST",
        data: {st: start_time, et: end_time,
            dt: date, cpty: capacity, t: token},
        datatype: 'json',
        success: function(response){
            if (state == "choose-room" || state == "booked") {
                console.log("Stale availability-request response received");
                return;
            }
            if (response == "logged-out") {
                get_login_token();
            } else if (response == "not-enough-info") {
                alert("There was a system error, please try again in a few seconds.");
            } else if (response == "no-rooms-available") {
                alert("There are no rooms available at the time you've selected. Please try another time.");
            } else {
                state = "choose-room";
                update_interface(response);
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
    var rooms = JSON.parse(response).rooms;

    const length = rooms.length;
    var element = '<select id="select_room" class="uArJ5e UQuaGc Y5sE8d guz9kb M9Bg4d">';
    for (var i = 0; i < length; i+=1) {
        element = element.concat('<option>');
        element = element.concat('<div>');
        element = element.concat( rooms[i].name)
        element = element.concat('</div>');
        element = element.concat('</option>')
        /*
        element = element.concat('<div>');
        element = element.concat( rooms[i].capacity)
        element = element.concat('</div>'); 
        */
    }

    element =element.concat( '</select>' );
    if ($('#tabEventDetails').length) {
        $("#tabEventDetails > div:nth-child(1)").after(element);
    }
}

function request_room(selected_room) {

    var Url = 'http://127.0.0.1:8080/book-room/';
    $.ajax({
        url: Url,
        type: "POST",
        data: {st: start_saved, et: end_saved,
            dt: date_saved, n: selected_room},
        datatype: 'json',
        success: function(response){
            if (state == "ready-to-book" || state == "booked") {
                console.log("Stale book-request response received");
                return;
            }
            if (response == "room-not-available") {
                alert("This room is no longer available, select a different one");
            } else {
                room_booked(response);
            }
            
        },
        error:function(error){
            alert('error');
        }
    });
}

function verify_event(eventId) {
    alert("verifying " + eventId);
    var Url = 'http://127.0.0.1:8080/booking/';
    $.ajax({
        url: Url,
        type: "POST",
        data: {id: eventId},
        datatype: 'json',
        success: function(response){
            var obj = JSON.parse(response);
            if (obj.valid == "valid") {
                state = "booked";
            } else if (obj.valid == "invalid") {
                state = "ready-to-book";
            }
            update_interface(obj.room);
        },
        error:function(error){
            alert('error');
        }
    });
}