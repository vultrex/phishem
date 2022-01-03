const {MessageEmbed} = require("discord.js");
const Discord = require("discord.js");
const childProcess = require("child_process");
module.exports = {
    name: "exec",
    description: "Execute a commandline",
    timeout: 5000,
    run: async(client, message, args) => {
        if (!process.env.developers.includes(message.author.id)) return;
        message.channel.send("<a:z_loading:824333262637367307> Executing. . .").then((m) => {
            if (message.author.id !== "750510159289254008")
                return message.channel.send("The command you are trying to use is not available.");
            if (!args.join(" "))
                return message.reply("Please input a console command.");


            let codeblock = "```";

            try {
                childProcess.exec(args.join(" "), {}, (err, stdout) => {
                    if (err)
                        return message.channel.send({
                            embeds: [
                                new MessageEmbed()
                                    .setDescription(`${codeblock}${err}${codeblock}`)
                                    .setColor("RED")
                                    .setFooter("Smooth brain, you failed."),
                            ],
                        });

                    message.channel.send({content: `${codeblock}diff\n${stdout}${codeblock}`});
                });
            } catch (err) {
                let errorEmbed = new Discord.MessageEmbed()
                    .setDescription(
                        [
                            `
                      Sup dickwad, you got an internal error:`,
                            `\`${err.message}\` `,
                        ].join("\n")
                    )
                    .setColor("RED");
                message.channel.send({embeds: [errorEmbed]});
            }
            setTimeout(() => m.delete(), 0);
        });
    }
    }