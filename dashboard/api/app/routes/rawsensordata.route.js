module.exports = app => {
    const rawSensorDatas = require("../controller/rawsensordata.controller.js");
    var router = require("express").Router();

    router.get('/get_all', rawSensorDatas.findAll);
    router.post('/', rawSensorDatas.create);
    app.use('/api/rawsensordata', router)
};