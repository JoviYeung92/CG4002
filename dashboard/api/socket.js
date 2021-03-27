const mysql = require('mysql');
var MySQLEvents = require('@rodrigogs/mysql-events');
var { socketIo } = require('./app');

const socketProgram = async () => {

    const connection = mysql.createConnection({
        // host: 'localhost',
        host: "localhost",
        user: 'capstone',
        port: 3306,
        // password: 'CG4002Weiyang1997!',
        password: 'capstone',
      });

    socketIo.on('connection', (client) => {
        console.log("new client: ", client.id);
        client.on('disconnect', () => {
            console.log("client disconnected");
        })
    })

    const instance = new MySQLEvents(connection, {
        startAtEnd: true, // to record only the new binary logs, if set to false or you didn'y provide it all the events will be console.logged after you start the app
        serverId: 10, 
    });

    await instance.start();

    /*
        To demo live streaming during evaluation
    */
    instance.addTrigger({
        name: 'monitoring live demo rawSensorData',
        expression: 'CG4002.liveRawSensorData', 
        statement: MySQLEvents.STATEMENTS.INSERT, 
        onEvent: e => {
            const data = e.affectedRows[0].after;
            socketIo.emit('demoRawSensorData', data);
        }
    });

    /*
        Real sensor data from ext. comms
    */
    instance.addTrigger({
        name: 'monitoring live rawSensorData',
        expression: 'CG4002.rawSensorData', 
        statement: MySQLEvents.STATEMENTS.INSERT, 
        onEvent: e => {
            const data = e.affectedRows[0].after;
            console.log(data);
            socketIo.emit('realRawSensorData', data);
        }
    });
    /*
       Real prediction data from ext. comms 
    */
    instance.addTrigger({
        name: 'monitoring live prediction',
        expression: 'CG4002.predictions', 
        statement: MySQLEvents.STATEMENTS.INSERT, 
        onEvent: e => {
            const data = e.affectedRows[0].after;
            socketIo.emit('realPrediction', data);
        }
    });

    /*
       Real FINAL prediction data from ext. comms 
    */
    instance.addTrigger({
        name: 'monitoring live prediction',
        expression: 'CG4002.finalpredictions', 
        statement: MySQLEvents.STATEMENTS.INSERT, 
        onEvent: e => {
            const data = e.affectedRows[0].after;
            socketIo.emit('realFinalPrediction', data);
        }
    });

    instance.on(MySQLEvents.EVENTS.CONNECTION_ERROR, console.error);
    instance.on(MySQLEvents.EVENTS.ZONGJI_ERROR, console.error);
};
module.exports = socketProgram