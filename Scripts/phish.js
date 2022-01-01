const fetch = require('node-fetch');
async function checkLink(link) {
    return await fetch("https://anti-fish.bitflow.dev/check", {
        method: "post",
        body: JSON.stringify({message: link}),
        headers: {
            "Content-Type": "application/json",
            "User-Agent": "Phish Systems (Nek#2937 / 750510159289254008)",
        },

    }).then(res => res.json())
}

async function linkInfo(domain) {
    return await fetch(`https://api.phisherman.gg/v1/domains/info/${domain}`, {
        headers: {
            "Authorization": 'Bearer 02e6fac0-b924-48aa-b583-2d410fbc691a',
            'Content-Type': 'application/json',
            "User-Agent": "Phish Systems (Nek#2937 / 750510159289254008)",
        },
    }).then(res => res.json())
}

async function checkYoutube(link) {
    const response = await require('node-fetch')(link).then(res => res.text())

    const linkHtmlCensors = ["discord nitro generator", "free nitro generator", "free discord nitro", "discord nitro code", "discord nitro codes",  "discord nitro codes generator"]
    return !!linkHtmlCensors.find(x => {
        const regex = new RegExp(`\\b${x}\\b`, 'i')
        return regex.test(response)
    })
}

module.exports = {
    checkLink,
    linkInfo,
    checkYoutube
}