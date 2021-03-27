module.exports = (sequelize, Sequelize) => {
    const FinalPrediction = sequelize.define("finalprediction", {
        Dancer1Prediction: {
            type: Sequelize.STRING
        },
        Dancer2Prediction: {
            type: Sequelize.STRING
        },
        Dancer3Prediction: {
            type: Sequelize.STRING
        },
        Dancer1Position: {
            type: Sequelize.INTEGER
        },
        Dancer2Position: {
            type: Sequelize.INTEGER
        },
        Dancer3Position: {
            type: Sequelize.INTEGER
        },
        SyncDelay: {
            type: Sequelize.FLOAT
        },
        Latency: {
            type: Sequelize.FLOAT
        }
    })
    return FinalPrediction
}