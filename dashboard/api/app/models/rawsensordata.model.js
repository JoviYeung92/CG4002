module.exports = (sequelize, Sequelize) => {
    const RawSensorData = sequelize.define("rawSensorData", {
        Roll: {
            type: Sequelize.FLOAT
        },
        Pitch: {
            type: Sequelize.FLOAT
        },
        Yaw: {
            type: Sequelize.FLOAT
        },
        GravitationalA1: {
            type: Sequelize.FLOAT
        },
        GravitationalA2: {
            type: Sequelize.FLOAT
        },
        GravitationalA3: {
            type: Sequelize.FLOAT
        },
        Dancer : {
            type: Sequelize.INTEGER
        }
    })
    return RawSensorData
}