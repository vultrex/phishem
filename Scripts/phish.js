const fetch = require('node-fetch');

/**
 *
 * @param link The link that will get checked.
 * @returns {Promise<any>}
 */
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

/**
 *
 * @param domain The domain link to check
 * @returns {Promise<any>}
 */
async function linkInfo(domain) {
    return await fetch(`https://api.phisherman.gg/v1/domains/info/${domain}`, {
        headers: {
            "Authorization": 'Bearer 02e6fac0-b924-48aa-b583-2d410fbc691a',
            'Content-Type': 'application/json',
            "User-Agent": "Phish Systems (Nek#2937 / 750510159289254008)",
        },
    }).then(res => res.json())
}

/**
 *
 * @param link A youtube link that'll get scanned
 * @returns {Promise<boolean>}
 */
async function checkYoutube(link) {
    return !![process.env.youtubeKeywords].find(async x => {
        const regex = new RegExp(`\\b${x}\\b`, 'i');
        return regex.test(await require('node-fetch')(link).then(res => res.text()))
    })
}

module.exports = {
    checkLink,
    linkInfo,
    checkYoutube
}