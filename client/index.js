
const express = require('express');
const path = require('path');
var session = require('express-session')
const axios = require('axios');
const app = express();
const port = 3000;
// const api = require('./api');
var routes = require('./router/routes')
require('dotenv').config({ path: path.join(__dirname,'../.env') })

var bodyParser = require('body-parser');

app.set('view engine', 'pug');
app.use(bodyParser.json()); // support json encoded bodies
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
app.use(express.static('public'))
app.use(session({
    secret:'Keep it secret'
    ,resave: false
    ,name:'uniqueSessionID'
    ,saveUninitialized:false
}))

app.use('/', routes);

app.listen(port, () => {
    console.log('Example app listening at http://localhost:3000');
})