module.exports = app => {
    const prediction = require("../controller/prediction.controller.js");
    var router = require("express").Router();

    router.post('/', prediction.create);
    app.use('/api/prediction', router)
};