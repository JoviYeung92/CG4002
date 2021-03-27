module.exports = app => {
    const statistics = require("../controller/statistics.controller.js");
    var router = require("express").Router();

    router.get('/get_all', statistics.findAll);
    router.post('/', statistics.create);
    app.use('/api/statistics', router)
};