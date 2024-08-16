const webpack = require('webpack');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from .env file
const envPath = path.resolve(__dirname, '../../../.env');
const env = dotenv.config({ path: envPath }).parsed;

// Print out the envPath and env value to verify correct loading
console.log(`Loading environment variables from: ${envPath}`);
console.log(env);

// Create an object that maps process.env variables for DefinePlugin
const envKeys = env ? Object.keys(env).reduce((prev, next) => {
  prev[`process.env.${next}`] = JSON.stringify(env[next]);
  return prev;
}, {}) : {};

