const { httpServer }  = require('./app');
const db = require("./app/models");
var socketProgram = require('./socket');

const port = process.env.API_PORT;
db.sequelize.sync();
db.sequelize.sync({ force: true }).then(() => {
  console.log("Drop and re-sync db.");
});

// for sending res to http server if needed
httpServer.listen(port, () => {
    console.log(`Server is listening on port: ${port}`);
    console.log(`Dashboard root url is ${process.env.DASHBOARD_ROOT_URL}`);
  });

// emitting real-time information via socket
socketProgram();