module.exports = app => {
    const finalprediction = require("../controller/finalprediction.controller.js");
    var router = require("express").Router();

    router.post('/', finalprediction.create);
    app.use('/api/finalprediction', router)
};