import gplay from 'google-play-scraper';
import fs from 'fs';

async function getApps() {
    console.log('Fetching apps from Google Play Store...');
    try {
        const results = await gplay.search({
            term: globalThis.sharedData.category,
            num: 100,
            lang: 'en',
            country: 'us'
        });

        console.log(`Found ${results.length} apps`);

        let appDetails = [];

        for (const result of results) {
            if (result.score <= 4.0) {
                console.log(`Processing app ${result.appId}`);
                try {
                    const appInfo = await gplay.app({ appId: result.appId });
                    appDetails.push({
                        Name: appInfo.title || 'N/A',
                        OS: 'Android',
                        Tag: globalThis.sharedData.category,
                        Rating: appInfo.score || 'N/A',
                        Downloads: appInfo.maxInstalls || 'N/A',
                        Review_Count: appInfo.ratings  || 'N/A',
                        Reviews: appInfo.ratings || 'N/A',
                        Country: '',
                        Release_date: appInfo.released || 'N/A',    
                        Developer: appInfo.developer || 'N/A',
                        link: `https://play.google.com/store/apps/details?id=${appInfo.appId}`,
                        devLink: appInfo.developerWebsite || 'N/A',
                        id: appInfo.appId
                    });
                } catch (error) {
                    console.error(`Failed to retrieve app details for ${result.appId}: ${error}`);
                }
            }
        }

        console.log(`Processed ${appDetails.length} apps`);
        return appDetails;

    } catch (error) {
        console.error(`Failed to search for apps: ${error}`);
        return [];
    }
}

async function getReviews(appId) {
    console.log(`Getting reviews for app ID: ${appId}`);
    try {
        const reviewList = [];
        const reviews = await gplay.reviews({
            appId: appId,
            sort: gplay.sort.NEWEST,
            num: 1000
        });

        reviews.data.forEach(review => {
            reviewList.push({
                user: review.userName,
                review: review.text,
                rating: review.score,
                date: new Date(review.date).toISOString()
            });
        });

        console.log(`Retrieved ${reviewList.length} reviews for app ID: ${appId}`);
        return reviewList;

    } catch (error) {
        console.error(`Failed to retrieve reviews for ${appId}: ${error}`);
        return [];
    }
}

function removeOldReviews(reviewList, monthsAgo) {
    const cutoffDate = new Date();
    cutoffDate.setMonth(cutoffDate.getMonth() - monthsAgo);

    const filteredReviews = reviewList.filter(review => new Date(review.date) >= cutoffDate)
        .map(review => ({
            ...review,
            date: new Date(review.date).toISOString()
        }));

    console.log(`Removed old reviews, ${filteredReviews.length} reviews remaining`);
    return filteredReviews;
}

function loadExistingData(filename) {
    if (fs.existsSync(filename)) {
        console.log('Loading existing data from JSON file');
        return JSON.parse(fs.readFileSync(filename, 'utf-8'));
    }
    return {};
}

async function saveDataToJson(apps, filename = 'apps.json') {
    try {
        console.log('Saving data to JSON file...');
        const existingData = loadExistingData(filename);

        for (const app of apps) {
            console.log(`Fetching reviews for app ID: ${app.id}`);
            const reviewList = await getReviews(app.id);
            const filteredReviews = removeOldReviews(reviewList, 3);

            app.Reviews = filteredReviews;

            existingData[app.id] = app;
        }

        fs.writeFileSync(filename, JSON.stringify(existingData, null, 4));
        console.log(`Data successfully saved to ${filename}`);

    } catch (error) {
        console.error(`Failed to write JSON file: ${error}`);
    }
}

export default async function main() {
    console.log("Starting gplay scraper...");
    const apps = await getApps();
    await saveDataToJson(apps);
    console.log("Finished gplay scraper.");
}