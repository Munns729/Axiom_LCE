const https = require('https');
const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.static('src'));

// For development, we'll use a self-signed certificate
// In production, use a proper SSL certificate
const options = {
    key: fs.readFileSync('localhost-key.pem'),
    cert: fs.readFileSync('localhost.pem')
};

https.createServer(options, app).listen(8080, () => {
    console.log('HTTPS Server running on https://localhost:8080');
    console.log('Serving files from ./src directory');
});
