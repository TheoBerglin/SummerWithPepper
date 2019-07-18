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
  $('#exit').click(exitButton);
  $('#bbc').click(launchBBC);
  $('#fotbollskanalen').click(launchFotbollskanalen);
  $('#reuters').click(launchReuters);
  $('#cbn').click(launchCBN);
  $('#bbc_tech').click(launchBBCTech);
  $('#bbc_business').click(launchBBCBusiness);
  $('#cnn').click(launchCNN);
  $('#fox').click(launchFOX);
});

function exitButton() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('exit_button_clicked', 1);
  }, function (error) {
    console.log(error);
  })
}

function launchBBC() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "bbc");
  }, function (error) {
    console.log(error);
  })
}

function launchFotbollskanalen() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "fotbollskanalen");
  }, function (error) {
    console.log(error);
  })
}

function launchReuters() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "reuters");
  }, function (error) {
    console.log(error);
  })
}

function launchCBN() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "cbn");
  }, function (error) {
    console.log(error);
  })
}

function launchBBCTech() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "bbc_tech");
  }, function (error) {
    console.log(error);
  })
}

function launchBBCBusiness() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "bbc_business");
  }, function (error) {
    console.log(error);
  })
}

function launchCNN() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "cnn");
  }, function (error) {
    console.log(error);
  })
}

function launchFOX() {
	session.service('ALMemory').then(function (memory) {
		memory.raiseEvent('news_clicked', "fox");
  }, function (error) {
    console.log(error);
  })
}