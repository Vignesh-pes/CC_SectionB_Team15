// screenshotHelper.js
// This script will generate JSON output to help you create screenshots
// showing the functionality of the application

const axios = require('axios');
const fs = require('fs');
const path = require('path');

const API_URL = 'http://localhost:3000/api';

// Function to nicely format and save API responses for screenshot purposes
const saveResponseForScreenshot = async (filename, requestFn) => {
  try {
    // Create screenshots directory if it doesn't exist
    const screenshotsDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir);
    }
    
    // Execute the request
    const response = await requestFn();
    
    // Format the response data for better readability
    const formattedData = JSON.stringify(response.data, null, 2);
    
    // Save to file
    const filePath = path.join(screenshotsDir, `${filename}.json`);
    fs.writeFileSync(filePath, formattedData);
    
    console.log(`Saved response to ${filePath}`);
    return response.data;
  } catch (error) {
    console.error(`Error generating screenshot for ${filename}:`, error.message);
  }
};

// Generate sample data
const generateSampleData = async () => {
  console.log('Generating sample data for screenshots...');
  
  // Sample user activities for different users
  const activities = [
    // User 1 - Regular user with various activities
    {
      userId: 'john_doe',
      action: 'login',
      details: { browser: 'Chrome', os: 'Windows', device: 'Desktop' }
    },
    {
      userId: 'john_doe',
      action: 'profile_update',
      details: { fields: ['name', 'email'], previousEmail: 'john@example.com', newEmail: 'john.doe@example.com' }
    },
    {
      userId: 'john_doe',
      action: 'permission_change',
      details: { newRole: 'editor', previousRole: 'viewer' }
    },
    {
      userId: 'john_doe',
      action: 'logout',
      details: { sessionDuration: '2h 15m' }
    },
    
    // User 2 - Admin performing administrative actions
    {
      userId: 'admin_user',
      action: 'login',
      details: { browser: 'Firefox', os: 'MacOS', device: 'Desktop' }
    },
    {
      userId: 'admin_user',
      action: 'account_creation',
      details: { createdUser: 'new_employee', userRole: 'editor' }
    },
    {
      userId: 'admin_user',
      action: 'permission_change',
      details: { targetUser: 'john_doe', newRole: 'admin', previousRole: 'editor', reason: 'promotion' }
    },
    
    // User 3 - Mobile user with some failed actions
    {
      userId: 'mobile_user',
      action: 'login',
      details: { browser: 'Safari', os: 'iOS', device: 'Mobile' }
    },
    {
      userId: 'mobile_user',
      action: 'failed_login',
      status: 'failure',
      details: { browser: 'Chrome', os: 'Android', device: 'Mobile', reason: 'incorrect_password', attemptCount: 1 }
    },
    {
      userId: 'mobile_user',
      action: 'password_change',
      details: { reason: 'user_requested' }
    },
    {
      userId: 'mobile_user',
      action: 'login',
      details: { browser: 'Chrome', os: 'Android', device: 'Mobile' }
    }
  ];
  
  // Create all activities
  for (const activity of activities) {
    try {
      await axios.post(`${API_URL}/activities`, activity);
      console.log(`Created activity: ${activity.userId} - ${activity.action}`);
    } catch (error) {
      console.error('Error creating activity:', error.message);
    }
  }
  
  console.log('Sample data generation completed');
};

// Generate screenshots for all major endpoints
const generateScreenshots = async () => {
  await generateSampleData();
  
  // Screenshot 1: Get all activity logs
  await saveResponseForScreenshot('01-all-activities', async () => {
    return await axios.get(`${API_URL}/activities`);
  });
  
  // Screenshot 2: Get specific user's activity
  await saveResponseForScreenshot('02-user-activities', async () => {
    return await axios.get(`${API_URL}/activities/user/john_doe`);
  });
  
  // Screenshot 3: Get activities by action type
  await saveResponseForScreenshot('03-login-activities', async () => {
    return await axios.get(`${API_URL}/activities/action/login`);
  });
  
  // Screenshot 4: Get failed activities
  await saveResponseForScreenshot('04-failed-activities', async () => {
    const response = await axios.get(`${API_URL}/activities`);
    const failedActivities = {
      data: response.data.data.filter(activity => activity.status === 'failure'),
      message: 'Filtered failed activities'
    };
    return { data: failedActivities };
  });
  
  // Screenshot 5: Get specific activity details
  await saveResponseForScreenshot('05-activity-details', async () => {
    // Get the first activity to use its ID
    const activitiesResponse = await axios.get(`${API_URL}/activities`);
    const firstActivityId = activitiesResponse.data.data[0]._id;
    return await axios.get(`${API_URL}/activities/${firstActivityId}`);
  });
  
  console.log('Screenshot data generation completed');
};

// Run the screenshot generator
generateScreenshots().catch(error => {
  console.error('Screenshot generation failed:', error.message);
});