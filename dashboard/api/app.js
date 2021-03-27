require('dotenv').config({path: __dirname + '/.env'});
const express = require('express');
const app = express();
const http = require('http');
const bodyParser = require('body-parser');
const cors = require('cors');

var corsOptions = {
  origin: process.env.DASHBOARD_ROOT_URL,
  optionsSuccessStatus: 200 // some legacy browsers (IE11, various SmartTVs) choke on 204
}
app.use(cors(corsOptions));

// parse requests of content-type - application/json
app.use(bodyParser.json());

// parse requests of content-type - application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));
require("./app/routes/rawsensordata.route")(app);
require("./app/routes/account.route")(app);
require("./app/routes/statistics.route")(app);
require("./app/routes/prediction.route")(app);
require("./app/routes/finalprediction.route")(app);

const httpServer = http.createServer(app);

// hooked to api server as a platform used for listening to clients
var socketIo = require('socket.io').listen(httpServer);

module.exports = { httpServer, socketIo };


