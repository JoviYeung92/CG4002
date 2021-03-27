module.exports = (sequelize, Sequelize) => {
    const Statistics = sequelize.define("statistics", {
        Username: {
            type: Sequelize.STRING
        },
        DanceMovePrediction: {
            type: Sequelize.BOOLEAN
        },
        DanceMove: {
            type: Sequelize.STRING
        },
        AverageRoll: {
            type: Sequelize.FLOAT
        },
        AveragePitch: {
            type: Sequelize.FLOAT
        },
        AverageYaw: {
            type: Sequelize.FLOAT
        },
        AverageA1: {
            type: Sequelize.FLOAT
        },
        AverageA2: {
            type: Sequelize.FLOAT
        },
        AverageA3: {
            type: Sequelize.FLOAT
        },
    })
    return Statistics
}