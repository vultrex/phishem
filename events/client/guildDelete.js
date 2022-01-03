const Schema = require("../../Database/Schema/Guild")

module.exports = async (client, guild) => {
    Schema.findOneAndDelete({ id: guild.id }, (err, res) => {
        if (err) console.log(err)
    })
}