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
  $('#go').click(goButton);
});

function changeTitle(data) {
  $('h1').text('Message received!')
}

function goButton() {
	session.service('ALMemory').then(function (memory) {
		var dep = document.getElementById('departure').value;
		var arr = document.getElementById('arrival').value;
		var timeControl = "";
        var selected = $("input[type='radio'][name='time_radio']:checked");
        if (selected.length > 0) {
            timeControl = selected.val();
        }
        memory.insertData('dep_stop', dep);
		memory.insertData('arr_stop', arr);
		memory.insertData('trip_time', timeControl);
		memory.raiseEvent('trip', 1);
  }, function (error) {
    console.log(error);
  })
}

var timepicker = new TimePicker('time', {
  lang: 'en',
  theme: 'dark'
});
timepicker.on('change', function(evt) {

  var value = (evt.hour || '00') + ':' + (evt.minute || '00');
  evt.element.value = value;

});

