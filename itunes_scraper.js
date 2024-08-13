import store from 'app-store-scraper';
import fs from 'fs';
import moment from 'moment';

async function fetchApps(num, pages, country, lang) {
    console.log('Fetching apps from Apple App Store...');
    let results = [];
    for (let i = 1; i <= pages; i++) {
        try {
            console.log(`Fetching page ${i}`);
            let apps = await store.search({
                term: globalThis.sharedData.category,
                num: num,
                page: i,
                country: country,
                lang: lang
            });

            for (const app of apps) {
                if (app.score && app.score < 4.5) {
                    let releaseDate = app.released ? moment(app.released).format('YYYY-MM-DD') : 'N/A';
                    results.push({
                        Name: app.title || 'N/A',
                        OS: 'iOS',
                        Tag: globalThis.sharedData.category,
                        Rating: app.score || 'N/A',
                        Downloads: 'N/A',
                        Review_Count: app.reviews || 'N/A',
                        Reviews: 'N/A',
                        Country: '',
                        Release_date: releaseDate,
                        Developer: app.developer || 'N/A',
                        link: app.url || 'N/A',
                        devLink: app.developerUrl || 'N/A',
                        id: app.appId || 'N/A'
                    });
                }
            }

        } catch (error) {
            console.log(`Error on page ${i}:`, error);
        }
    }
    console.log(`Fetched ${results.length} apps`);
    return results;
}
async function getReviews(appId) {
    console.log(`Getting reviews for app ID: ${appId}`);
    let reviewList = [];
    let previousReviewCount = 0;
    const threeMonthsAgo = moment().subtract(3, 'months');

    try {
        for (let page = 1; page < 11; page++) {
            let reviews = await store.reviews({
                appId: appId,
                sort: store.sort.RECENT,
                page: page
            });

            reviews.forEach(review => {
                let reviewDate = moment(review.updated);
                if (reviewDate.isAfter(threeMonthsAgo)) {
                    reviewList.push({
                        user: review.userName,
                        review: review.text,
                        rating: review.score,
                        date: reviewDate.toISOString()
                    });
                }
            });

            console.log(`Retrieved ${reviewList.length} reviews for app ID: ${appId}`);       

            if (reviewList.length === previousReviewCount) {
                console.log(`No new reviews on page ${page}, stopping further requests.`);
                break;
            }

            previousReviewCount = reviewList.length;
        }
    } catch (error) {
        console.log(`Failed to retrieve reviews: ${error}`);
    }
    return reviewList;
}


function saveToJsonFile(data, filename) {
    fs.writeFileSync(filename, JSON.stringify(data, null, 4), 'utf-8');
    console.log(`Data saved to ${filename}`);
}

async function saveDataToJson(apps, filename = 'apps.json') {
    try {
        console.log('Saving data to JSON file...');
        let existingData = {};

        if (fs.existsSync(filename)) {
            existingData = JSON.parse(fs.readFileSync(filename, 'utf-8'));
            console.log("Loaded existing data from JSON.");
        }

        for (let app of apps) {
            console.log(`Fetching reviews for app ID: ${app.id}`);
            let reviewList = await getReviews(app.id);

            app.Reviews = reviewList.length > 0 ? reviewList : 'N/A';

            existingData[app.id] = app;
        }

        saveToJsonFile(existingData, filename);
        console.log(`JSON file ${filename} written successfully.`);
    } catch (error) {
        console.log(`Failed to write JSON file: ${error}`);
    }
}

export default async function main() {
    console.log("Starting itunes scraper...");
    let apps = await fetchApps(200, 1, 'us', 'en');
    await saveDataToJson(apps);
    console.log("Finished itunes scraper.");
}