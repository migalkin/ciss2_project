/**
 * 
 */
var intervalKey;



function startInterval(functionToExecute){
	intervalKey = setInterval(function() {
		functionToExecute
	}, config.interval);
}

function timedCount() {
	
  counterSinceLast = counterSinceLast + 1;
  timeCountSinceLast = setTimeout(timedCount, 1000);
  // console.log("counterSinceLast", counterSinceLast);
   
  if(AppConfig.video == "video"){
	  if(counterSinceLast === 40) {
	    trigger('8');
	  }
	  if(counterSinceLast === 80) {
		  goToNext();
	  }
	  
  }else{	  
	  if(counterSinceLast === 40) {
		    trigger('8');
	  }
	  if(counterSinceLast === 80) {
	    if($('.slick-current').attr('next-uri')) {
	      $('.autoplay').slick('slickNext');
	    } else {
	      trigger('4');
	    }
	  }
  }
}

function goToNext() {
	stopCount();
	if(Pictures[picInx].next_uri) {
		video.currentTime = Pictures[picInx].end_time;
		picInx ++;
		if(video.paused){
			video.play();
		}
		timedCount();
	} else {
		trigger('4');
	}
}

function restartCount() {	
  stopCount();
  console.log('Restarting Counter')
  timedCount();
}

function stopCount() {
  console.log('Stopping Counter')
  clearTimeout(timeCountSinceLast);
  counterSinceLast = 0;
}

