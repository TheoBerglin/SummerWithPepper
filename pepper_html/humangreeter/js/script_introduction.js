// keeping a pointer to the session is very useful!
var session;

try {
  QiSession( function (s) {
    console.log('connected!');
    session = s;
    // now that we are connected, we can use the buttons on the page
    $('button').prop('disabled', false);
    /*s.service('ALMemory').then(function (memory) {
      memory.subscriber('TouchChanged').then(function (subscriber) {
        subscriber.signal.connect(changeTitle);
      });
    });*/
  });
} catch (err) {
  console.log("Error when initializing QiSession: " + err.message);
  console.log("Make sure you load this page from the robots server.")
}

$(function () {
  $('#vasttrafik').click(introduceVasttrafik);
  $('#weather').click(introduceWeather);
  /*$('#vasttrafik2').click(introduceVasttrafik2);*/
});

function changeTitle(data) {
  $('h1').text('Message received!')
}

function introduceVasttrafik() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('vt', 1);
  }, function (error) {
    console.log(error);
  })
  /*
  session.service('ALTextToSpeech').then(function (tts) {
    tts.say('Do you want to plan a trip or see next departures?');
  }, function (error) {
    console.log(error);
  })
  */
}

function introduceWeather() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('weather', 1);
  }, function (error) {
    console.log(error);
  })
}