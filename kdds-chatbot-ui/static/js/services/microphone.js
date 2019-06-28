/**
 * This code handles all interactions concerning the microphone activation and button behaviour
 */

/**
 * Initialize the microphone when the page finished loading
 * @returns
 */
var dictate;
var isConnected = false;
startPosition = 0;
endPosition = 0;

function initMsgBoxPositions(){
	startPosition = $("#msg_input").prop("selectionStart");
	endPosition = startPosition;
}

$(document).ready(function() {
	// Initialize dictate and callbacks of the backend communication
	initializeMicrophone()
	dictate.init()	
	dictate.cancel();
	
	// Enable Microphone button
	$("#start").on( 'click', toggleListening );
});

/**
 * Event fired when the connection to speech recognition service is activated. 
 */
readyForSpeech = function(){
	// mark connection as established
	isConnected = true;	
	changeButtonToListening();
	__message("READY FOR SPEECH");
	initMsgBoxPositions()
	
    //stop counter for trigger
    stopCount();
    
	// Unclear what this is used for
	var textBeforeCaret = $("#msg_input").val().slice(0, startPosition);
	if ((textBeforeCaret.length == 0) || /\. *$/.test(textBeforeCaret) ||  /\n *$/.test(textBeforeCaret)) {
		doUpper = true;
	} else {
		doUpper = false;
	}
	doPrependSpace = (textBeforeCaret.length > 0) && !(/\n *$/.test(textBeforeCaret));
	
	initHotword();	
}

/**
 * Initialized the usage of a hotword
 * @returns
 */
function initHotword(){
	hotword = $("#hotword").val();
    per_segment_hotword = $('#per_segment_hotword').prop('checked')            
    if (hotword && hotword.length > 0) {
    	// EISKDDS-176 for now this code is unreachable, until we make the input box for hotwords enabled for debugging purposes
        dictate.setHotword(hotword, per_segment_hotword);
    }else{
    	// EISKDDS-176 To not confuse the user, we remove the input box for the hotwords
    	hotword = appConfig.hotword.hotword
    	var perSegment = appConfig.hotword.perSegment.toLowerCase() === "true"? true : false
    	dictate.setHotword(hotword, perSegment);
    }
}

/**
 * Upon the end of a speech segment, this function is called
 */
endOfSpeech = function(){
	// speech input ended, though there is no need to end the connection
	__message("END OF SPEECH");
}

/**
 * We terminate the connection to the speech recognizer.
 */
endOfSession = function(){
	
//	if(isConnected){
//		console.log('Ending connection due to end of session')
//		endConnection();
//	}else{
//		console.log('Connection is already terminated, nothing more to do')
//	}	
	__message("END OF SESSION");	
}

/**
 * 
 */
checkForHotword = function(item){
	if(item.status === 10){
		console.log('Maybe a hotword was recognized')
		if(item.message === "Hotword detected! Listening!"){
			markKeywordAsDetected();
			stopSophiasVoiceOutput();
			stopCount();
			var timeout = 2500;
			hotWordResetTimeout = setTimeout(function() { 
					dictate.resetHotword(); 
					changeButtonToListening();
					restartCount();
				}, timeout);
		}
	}
}

/**
 * This function is called upon changes in the server status
 */
serverStatus = function(json){
	__serverStatus(json.num_workers_available);
	$("#serverStatusBar").toggleClass("highlight", json.num_workers_available == 0);
	// If there are no workers and we are currently not connected
	// then disable the Start/Stop button.
	if (json.num_workers_available == 0 && ! isConnected) {
		$("#start").prop("disabled", true);
	} else {
		$("#start").prop("disabled", false);
	}
}

/** 
 * This function is called upon receiving partial results
 */
partialResults = function(temporaryHypothesis){	
	clearTimeout(hotWordResetTimeout)
	stopCount();
	if(appConfig.disableOutputOfIntermediateResults.toLowerCase() == "true"){
		temporaryHypothesis = ".. transcribing";
		updateInputBox(temporaryHypothesis);
	}else{
		updateInputBox(temporaryHypothesis[0].transcript);
	}	
}


/**
 * Final result of the speech recognition segment
 */
results = function(hypothesis){
	clearTimeout(hotWordResetTimeout)
	
	if(hypothesis[0].transcript != ""){
		var msg = setInputBox(hypothesis[0].transcript)
		showUserMessage(msg);
		generateSpeechAssistentAnswer(msg, PoiId, SessionId);
		clearInputBox();
		changeButtonToListening()
		dictate.resetHotword();
		dictate.startListening(); // start again
	}else{
		clearInputBox();
		changeButtonToListening()
		dictate.resetHotword();
		dictate.startListening(); // start again
		console.log('Received empty result from speech recognizer')
	}
	
}

/** 
 * Function to be called upon an error
 */
error = function(code, data) {
	
	if(isConnected){
		console.log('Ending connection due to error: ' + code + ' data: ' + data)
		endConnection()
	}else{
		console.log('Connection already terminated: ' + code + ' data: ' + data)
	}
	
	// TODO: show error in the GUI
}

event = function(code, data) {
	console.log('code: ' + code + " data: " + data)
}

//TODO check if they are still need Private methods (called from the callbacks)
function __message(code, data) {
	//log.innerHTML = "msg: " + code + ": " + (data || '') + "\n" + log.innerHTML;
}

function __error(code, data) {
	//log.innerHTML = "ERR: " + code + ": " + (data || '') + "\n" + log.innerHTML;
}

function __serverStatus(msg) {
	//serverStatusBar.innerHTML = msg;
}

/**
 * Public methods (called from the GUI)
 * @returns
 */
function toggleListening() {
	console.log('Microphone toggling clicked')
	clearKeyboardInputField();

	if (isConnected) {
		endConnection()
	} else {
		dictate.startListening();
	}
}

/**
 * Changing microphone button to "listening button"
 * @returns
 */
function changeButtonToListening(){	
	$("#start").removeClass();
	$("#start").addClass('end');
}

/**
 * Restore microphone button to initial state (showing mic)
 * @returns
 */
function changeButtonToNOTListening(){	
	$("#start").removeClass();
	$("#start").addClass('start');
}

/**
 * Change mic button to error
 */
function changeButtonToError(){	
	$("#start").removeClass();
	$("#start").addClass('error');
}

/**
 * Clears the input field
 * @returns
 */
function clearKeyboardInputField(){
	$("#msg_input")[0].textContent = "";
	$("#msg_input").val("");
	// needed, otherwise selectionStart will retain its old value
	$("#msg_input").prop("selectionStart", 0);
	$("#msg_input").prop("selectionEnd", 0);
}

/**
 * Highlights the microphone button in green
 * @returns
 */
function markKeywordAsDetected(){
	$("#start").removeClass()
	$("#start").addClass('active');
}

/**
 * End the connection between the website and the speech recognizer
 * @returns
 */
function endConnection(){	
	isConnected = false;
	changeButtonToNOTListening();
	dictate.cancel();
}

/** 
 * Initializes the micropohone and speech recognizer connection
 * @returns
 */
function initializeMicrophone(){
	var recorderWorkerPath = "/static/js/recorderWorker.js"
	if(AppConfig.video.toLowerCase() == "true"){
		recorderWorkerPath = "/video/js/recorderWorker.js"
	}
	options = {
			server : speechSrv.speech,
			serverStatus : speechSrv.status,
			recorderWorkerPath : recorderWorkerPath,
			onReadyForSpeech: readyForSpeech,
			onEndOfSpeech: endOfSpeech,
			onEndOfSession: endOfSession,
			onServerStatus: serverStatus,
			onPartialResults: partialResults,
			onResults: results,
			onError: error,
			onEvent : event
	}
	dictate = new Dictate(options)
}