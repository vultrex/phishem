const userSchema = require("../../Database/Schema/User");
module.exports = {
    name: "reset",
    timeout: 5000,
    run: async(client, msg, args) => {
        if (!process.env.developers.includes(msg.author.id)) return;
        const id = args.join(" ");
        if(isNaN(id)) return msg.channel.send("Please enter a valid user id");
        userSchema.findOne({user_id: id}, async (err, data) => {
            if(!data) return msg.reply({content: "This user has no infractions."})
            else {
                userSchema.findOneAndDelete({user_id: id}, (err, data) => {
                    if(err) return msg.reply("Looks like an an error occurred.")
                    else return msg.reply("User has been reset.")
                })
            }
        })
    }
    }