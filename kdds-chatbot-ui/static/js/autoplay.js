var SessionId;
var PoiId;
var timeCountSinceLast;  // time since last talk from user
var counterSinceLast = 0;  // counter for timeSinceLastInteraction
// var timeCountPoi;  // time in current Poi after silence trigger
// var counterPoi = 0;  // counter for Poi after silence trigger
var picInx = 0; //

//$(document).ready(function(){
$(function() {

  requestSessionId();
  
  if(AppConfig.video.toLowerCase() == "true"){
	  $(".audio-related").remove();
	  $(".video-related")[0].style.display = "block";
	  var video = document.getElementById("video");
	  video.play();
	  video.ontimeupdate = function() {
		  //console.log("CT", video.currentTime);
		  //console.log("MT", Pictures[picInx].blink_time - video.currentTime);
		  if(Pictures[picInx].blink_time - video.currentTime <= 1) {
			  video.pause();
		  }
	  }
	  


  }else {
	  $(".video-related").remove();
	  $(".audio-related")[0].style.display = "block";
	  slickSetup();
	  
  }
  
  setTimeout(function(){trigger((Math.round(Math.random())+1).toString())}, 1000);
  setTimeout(function(){trigger('3')}, 15000);
  setTimeout(function(){timedCount()}, 21000);
});



function slickSetup() {
  $('.autoplay').slick({
    slidesToShow: 1,
    slidesToScroll: 1,
    speed: 3000,
    arrows: false,
    infinite: false
  }).on("afterChange", function(e, slick) {
    restartCount();
    // restartCountPoi();
  });
}

