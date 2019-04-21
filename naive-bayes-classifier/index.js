'use strict';
const express = require('express');
const bodyParser = require('body-parser');
const app = express();

app.set('port', 1504);
app.use(bodyParser.json());

app.get('/', function(req, res){
    res.send('Server is Up!');
})

const classifier =require('./ai.js').classifier();
app.post('/classify/', function(req, res){
    var data=req.body;
    var count = 0;
    for(var i =0; i<data.texts.length; i++) {
        try{
            var messageString=data.texts[i].textMessage;
            data.texts[i].cat = classifier.categorize(messageString);
            count++;
       }catch(e){
        console.log(e);
       }
    }
    console.log(count+" classified out of "+data.texts.length);
    res.status(200).send(data);
 });

// Spin up the server
app.listen(app.get('port'), function(){
        console.log('running on port', app.get('port'));
    });