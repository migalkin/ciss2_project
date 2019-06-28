/**
 * 
 */

/** Requests the sessionID from the backend
 * 
 * @returns Nothing
 */
function requestSessionId() {
	  $.ajax({
	    type: "GET",
	    url: 'http://127.0.0.1:5000/',
	    success: function(results) {
	    	SessionId = results.sid;
	    	console.log("Session id: ", SessionId);
	      
	    },
	    error: function(error) {
	      console.log("ERROR, Failed to get session id: " + error);	      
	    }
	  });
	}


function askbackend(text){
	$.ajax({
		url: 'http://127.0.0.1:5000/',
		type: "POST",
		data: text,
		dataType: "text",
		success: function(results) {
		showBotMessage(results);
		},
	});
}
