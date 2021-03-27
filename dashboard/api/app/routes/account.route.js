module.exports = app => {
    const accounts = require("../controller/account.controller.js");
    var router = require("express").Router();

    router.post('/authenticate', accounts.authenticate);
    router.post('/', accounts.create);
    app.use('/api/account', router)
};