const db = require("../models");
const FinalPrediction = db.finalprediction;
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
        Dancer1Prediction: req.body.Dancer1Prediction,
        Dancer2Prediction: req.body.Dancer2Prediction,
        Dancer3Prediction: req.body.Dancer3Prediction,
        Dancer1Position: req.body.Dancer1Position,
        Dancer2Position: req.body.Dancer2Position,
        Dancer3Position: req.body.Dancer3Position,
        SyncDelay: req.body.SyncDelay,
        Latency: req.body.Latency
    }
    FinalPrediction.create(data)
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500)
        })
};
