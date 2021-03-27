const db = require("../models");
const Statistics = db.statistics;
const Op = db.Sequelize.Op;

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
        DanceMovePrediction: req.body.DanceMovePrediction,
        DanceMove: req.body.DanceMove,
        AverageRoll: req.body.AverageRoll,
        AveragePitch: req.body.AveragePitch,
        AverageYaw: req.body.AverageYaw,
        AverageA1: req.body.AverageA1,
        AverageA2: req.body.AverageA2,
        AverageA3: req.body.AverageA3,
    }
    Statistics.create(data)
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500)
        })
};

exports.findAll = (req, res) => {
    const Username = req.query.Username;
    console.log("Username", Username)
    var condition = Username ? { Username: { [Op.like]: `%${Username}%` } } : null;
    Statistics.findAll({where: condition})
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500);
        })
};
