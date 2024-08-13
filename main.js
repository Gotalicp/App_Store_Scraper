globalThis.sharedData = {
    category: 'Entertainment'
};

console.log("Initializing main script...");

import('./gplay_scraper.js')
    .then(module => {
        console.log("Starting Google Play scraper...");
        return module.default();
    })
    .then(() => import('./itunes_scraper.js'))
    .then(module => {
        console.log("Starting Apple App Store scraper...");
        return module.default();
    })
    .then(() => {
        console.log("All scrapers finished.");
    })
    .catch(error => console.error(`Error executing scripts: ${error}`));
