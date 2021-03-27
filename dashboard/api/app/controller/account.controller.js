const db = require("../models");
const Account = db.accounts;
const Op = db.Sequelize.Op;

exports.authenticate = (req, res) => {
    const username = req.body.Username;
    const password = req.body.Password;
    if (username === "" || password === "") {
        res.sendStatus(401);
        return
    }
    const condition = {Username: {[Op.like]: `%${username}%`}, Password: {[Op.like]: `%${password}`}}
    Account.findAll({where: condition})
        .then(data => {
            res.send(data);
        })
        .catch(err => {
            res.sendStatus(500);
        })
};

exports.create = (req, res) => {
    console.log(req.body);
    if (!req.body) {
        res.status(400).send({
            message: "Content can't be empy!"
        });
        return;
    }
    const data = {
        Username: req.body.Username,
        Password: req.body.Password,
    }
    Account.create(data)
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(402)
        })
};