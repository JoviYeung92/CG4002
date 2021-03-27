const db = require("../models");
const RawSensorData = db.rawSensorDatas;
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
        Roll: req.body.Roll,
        Pitch: req.body.Pitch,
        Yaw: req.body.Yaw,
        GravitationalA1: req.body.GravitationalA1,
        GravitationalA2: req.body.GravitationalA2,
        GravitationalA3: req.body.GravitationalA3,
        Dancer: req.body.Dancer
    }
    RawSensorData.create(data)
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500)
        })
};

exports.findAll = (req, res) => {
    const Dancer = req.query.Dancer;
    var condition = Dancer ? { Dancer: { [Op.like]: `%${Dancer}%` } } : null;
    RawSensorData.findAll({where: condition})
        .then(data => {
            res.send(data)
        }).catch(err => {
            res.sendStatus(500);
        })
};
