module.exports = (sequelize, Sequelize) => {
    const Account = sequelize.define("account", {
        Username: {
            type: Sequelize.STRING,
            unique: true
        },
        Password : {
            type: Sequelize.STRING
        }
    })
    return Account
}