import FormData from 'form-data';
import fs from 'fs';
import path from 'path';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

async function testEndpoint(name, url, options) {
  console.log(`\n--- Testing: ${name} ---`);
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(data)}`);
    }
    console.log('Status:', response.status);
    console.log('Response:', data);
    console.log(`✅ ${name} PASSED`);
    return true;
  } catch (error) {
    console.error(`❌ ${name} FAILED:`, error.message);
    return false;
  }
}

async function main() {
  let allTestsPassed = true;
  
  // Test 1: GET /ml/models/regression
  const regressionModelsUrl = `${BASE_URL}/ml/models/regression`;
  if (!await testEndpoint('Get Regression Models', regressionModelsUrl, { method: 'GET' })) {
    allTestsPassed = false;
  }

  // Test 2: POST /ml/get_columns
  const getColumnsUrl = `${BASE_URL}/ml/get_columns`;
  const form = new FormData();
  const filePath = path.resolve(process.cwd(), 'public/sample.csv');
  if (!fs.existsSync(filePath)) {
    console.error(`\n❌ Could not find sample.csv at ${filePath}. Skipping 'Get Columns' test.`);
    allTestsPassed = false;
  } else {
    form.append('file', fs.createReadStream(filePath));
    if (!await testEndpoint('Get CSV Columns', getColumnsUrl, { method: 'POST', body: form })) {
      allTestsPassed = false;
    }
  }

  // Test 3: POST /simulation/simulation
  const simulationUrl = `${BASE_URL}/simulation/simulation`;
  const simulationPayload = {
    equation: 'Linear Motion (y = m*x + c)',
    x_min: 0,
    x_max: 10,
    variables: { m: 2, c: 1 },
  };
  if (!await testEndpoint('Run Simulation', simulationUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(simulationPayload),
  })) {
    allTestsPassed = false;
  }
  
  console.log('\n--- Smoke Test Summary ---');
  if (allTestsPassed) {
    console.log('✅ All smoke tests passed!');
    process.exit(0);
  } else {
    console.log('❌ Some smoke tests failed. Please check the backend server and configuration.');
    process.exit(1);
  }
}

main();
