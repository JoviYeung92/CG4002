const db = require("../models");
const Prediction = db.prediction;
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
        DanceMovePrediction: req.body.DanceMovePrediction,
        PositionPrediction: req.body.PositionPrediction,
        DancerNumber: req.body.DancerNumber,
    }
    Prediction.create(data)
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500)
        })
};
