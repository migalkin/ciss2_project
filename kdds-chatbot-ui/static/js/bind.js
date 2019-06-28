var data=[];

function addBr(text){
console.log(text);
    return text.replace(/\n/g, "<br />");

}

function processSyn(msg){
    console.log("Before processing: ", msg)
    for (var key in Synthesis){
        if (msg.includes(key)){
            msg = msg.replace(new RegExp("[\\" + key + "]", "g"), Synthesis[key]);
        }
    }
    console.log("After processing: ", msg);
    return msg
}

var Message;
Message = function (arg) {
console.log('MessageFunc');
    console.log(arg);
    this.text = arg.text, this.message_side = arg.message_side;
    this.draw = function (_this) {
        return function () {
            var $message;
            $message = $($('.message_template').clone().html());
            $message.addClass(_this.message_side).find('.text').html(addBr(_this.text));
            $('.messages').append($message);
            return setTimeout(function () {
                return $message.addClass('appeared');
            }, 0);
        };
    }(this);
    return this;
};

stopSophiasVoiceOutput = function(){
	audioPlayerElement = document.getElementById("audioPlayer")
	if(audioPlayerElement){
		audioPlayerElement.src = "";
	}
}

function showBotMessage(msg){
        message = new Message({
             text: msg,
             message_side: 'left'
        });
        audioPlayerElement = document.getElementById("audioPlayer")
        if(audioPlayerElement){
        	audioPlayerElement.src=AppConfig.tts+'='+encodeURIComponent(processSyn(msg));
        	
        	audioPlayerElement.onplaying = function(){        		        		
        		stopCount();
        	}
        	
        	audioPlayerElement.onended = function(){
        		restartCount();
        	}
        }
        
        message.draw();
        $messages = $('.messages');
        $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
}

/** 
 * Displays the users input in the user interface
 * @param msg
 * @returns
 */
function showUserMessage(msg){
        console.log('showUserMessage');
        $messages = $('.messages');
        message = new Message({
            text: msg,
            message_side: 'right'
        });
        message.draw();
        $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
        $('#msg_input').val('');
}



getMessageText = function () {
           console.log('getMessageText');

            var $message_input;

            $message_input = $('.message_input');
            return $message_input.val();
        };


$('.send_message').click(function (e) {
        msg = getMessageText();
        if(msg){
            showUserMessage(msg);
            //generateSpeechAssistentAnswer(msg);
            askbackend(msg);
            $('.message_input').val('');
        }
});

$('.message_input').keyup(function (e) {
    if (e.which === 13) {
        msg = getMessageText();
        if(msg){
        showUserMessage(msg);
        askbackend(msg);
        //generateSpeechAssistentAnswer(msg);
    $('.message_input').val('') ;}
    }
});

$('#stop_speak').click(function(e){
    msg = ''
    //document.getElementById("audioPlayer").src=AppConfig.tts+'='+msg
    document.getElementById("audioPlayer").pause()
});
