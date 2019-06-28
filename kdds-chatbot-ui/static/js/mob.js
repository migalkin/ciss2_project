// Global UI elements:
//  - log: event log
//  - trans: transcription window

// Global objects:
//  - tt: simple structure for managing the list of hypotheses
//  - dictate: dictate object with control methods 'init', 'startListening', ...
//       and event callbacks onResults, onError, ...

var tt = new Transcription();

var doUpper = false;
var doPrependSpace = true;

var appConfig = AppConfig
var speechSrv = appConfig.speechRecogSrv
var qaSrv = appConfig.questionAnsSrv


function clearInputBox(){
	$('#msg_input').val('');
}

function updateInputBox(input){
	inputText = prettyfyHyp(input, doUpper, doPrependSpace);
	$("#msg_input").val(inputText)
//	val = $("#msg_input").val();
//	$("#msg_input").val(val.slice(0, startPosition) + inputText + val.slice(endPosition));
//	endPosition = startPosition + inputText.length;
//	$("#msg_input").prop("selectionStart", endPosition);
}

function setInputBox(input){
	$('#msg_input').val('');
	inputText = prettyfyHyp(input, doUpper, doPrependSpace);
	val = $("#msg_input").val();
	$("#msg_input").val(val.slice(0, startPosition) + inputText + val.slice(endPosition));
	startPosition = startPosition + inputText.length;
	endPosition = startPosition;
	$("#msg_input").prop("selectionStart", endPosition);
	if (/\. *$/.test(inputText) ||  /\n *$/.test(inputText)) {
		doUpper = true;
	} else {
		doUpper = false;
	}
	doPrependSpace = (inputText.length > 0) && !(/\n *$/.test(inputText));
	var formattedInput = $("#msg_input").val()
	return formattedInput
}

function capitaliseFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function prettyfyHyp(text, doCapFirst, doPrependSpace) {
	if (doCapFirst) {
		text = capitaliseFirstLetter(text);
	}
	tokens = text.split(" ");
	text = "";
	if (doPrependSpace) {
		text = " ";
	}
	doCapitalizeNext = false;
	tokens.map(function(token) {
		if (text.trim().length > 0) {
			text = text + " ";
		}
		if (doCapitalizeNext) {
			text = text + capitaliseFirstLetter(token);
		} else {
			text = text + token;
		}
		if (token == "." ||  /\n$/.test(token)) {
			doCapitalizeNext = true;
		} else {
			doCapitalizeNext = false;
		}
	});

	text = text.replace(/ ([,.!?:;])/g,  "\$1");
	text = text.replace(/ ?\n ?/g,  "\n");
	return text;
}