// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';
var CALLBACK_URL = 'https://'+chrome.runtime.id+'.chromiumapp.org/';
var AUTH_URL = 'file:///C:/Users/gokhales/Documents/college/sp19/unanimous/ajgokhale.github.io/index.html?redirect_uri='+CALLBACK_URL;
AUTH_URL = 'https://ajgokhale.github.io/?redirect_uri=' + CALLBACK_URL;

var login_token = "null";
/*
chrome.runtime.onInstalled.addListener(function() {
  chrome.storage.sync.set({color: '#3aa757'}, function() {
    console.log('The color is green.');
  });
  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
        pageUrl: {hostEquals: 'developer.chrome.com'},
      })],
      actions: [new chrome.declarativeContent.ShowPageAction()]
    }]);
  });
});
*/

function send_token(sendResponse, token) {
  if (token != null) {
    chrome.storage.local.set({t: token}, function(result){
      console.log("The current token is " + token);
    });
    sendResponse({success: "success", t: token});
  } else {
    sendResponse({success: "failed"});
  }
}

function authenticate(sendResponse) {

  chrome.identity.launchWebAuthFlow({
        url: AUTH_URL,
        interactive: true,
      }, function(redirectURL) {
        var token = null;

        if (redirectURL) {
          var q = redirectURL.substr(redirectURL.indexOf('?')+1);
          var parts = q.split('&');
          for (var i = 0; i < parts.length; i++) {
            var kv = parts[i].split('=');
            if (kv[0] == 'access_token') {
              token = kv[1];
            }
          }
        }
      
        send_token(sendResponse, token);
      });
}

chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    authenticate(sendResponse);
    return true;
  });