const Schema = require("../../Database/Schema/Guild")
module.exports = async (client, guild) => {
    Schema.findOne({id: guild.id}, async (err, data) => {
        if(err) console.log(err)
        if(!data) {
            const newData = new Schema({
                id: guild.id
            })
            await newData.save()
        }
    })
    await require(`../../slash.js`)()
}