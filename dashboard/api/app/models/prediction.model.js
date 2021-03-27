module.exports = (sequelize, Sequelize) => {
    const Prediction = sequelize.define("prediction", {
        DanceMovePrediction: {
            type: Sequelize.STRING
        },
        PositionPrediction: {
            type: Sequelize.INTEGER
        },
        DancerNumber: {
            type: Sequelize.INTEGER
        },
    })
    return Prediction
}