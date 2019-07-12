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
  $('#goodButton').click(goodButton);
  $('#neutralButton').click(neutralButton);
  $('#badButton').click(badButton);
  $('#doneButton').click(doneButton);
});


function goodButton() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('good_button_click', 1);
  }, function (error) {
    console.log(error);
  })
}


function neutralButton() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('neutral_button_click', 1);
  }, function (error) {
    console.log(error);
  })
}


function badButton() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('bad_button_click', 1);
  }, function (error) {
    console.log(error);
  })
}

function doneButton() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('done_button_click', 1);
  }, function (error) {
    console.log(error);
  })
}