const dbConfig = require("../../dbconfig");
const Sequelize = require("sequelize");
const sequelize = new Sequelize(dbConfig.DB, dbConfig.USER, dbConfig.PASSWORD, {
  logging: false,
  host: dbConfig.HOST,
  dialect: dbConfig.dialect,
  operatorsAliases: false,
  port: dbConfig.PORT,

  pool: {
    max: dbConfig.pool.max,
    min: dbConfig.pool.min,
    acquire: dbConfig.pool.acquire,
    idle: dbConfig.pool.idle
  }
});

const db = {};

db.Sequelize = Sequelize;
db.sequelize = sequelize;
db.accounts = require("./account.model")(sequelize, Sequelize);
db.rawSensorDatas = require("./rawsensordata.model")(sequelize, Sequelize);
db.prediction = require("./prediction.model")(sequelize, Sequelize);
db.finalprediction = require("./finalprediction.model")(sequelize, Sequelize);
db.statistics = require("./statistics.model")(sequelize, Sequelize);
module.exports = db;