// script.js

// ================= API CONFIGURATION =================
// Change this to match your backend server URL
const API_BASE_URL = 'https://titanbackend.online';

// ================= PAGE NAVIGATION =================
function showPage(pageId) {
  const pages = document.querySelectorAll(".page");
  pages.forEach(page => {
    page.classList.toggle("active", page.id === pageId);
  });
}

// Navigation button handlers
document.querySelectorAll(".next-button").forEach(button => {
  button.addEventListener("click", () => {
    const nextPage = button.getAttribute("data-next");
    if (nextPage) {
      showPage(nextPage);
    }
  });
});

document.querySelectorAll(".back-button").forEach(button => {
  button.addEventListener("click", () => {
    const prevPage = button.getAttribute("data-prev");
    if (prevPage) {
      showPage(prevPage);
    }
  });
});

// ================= PREFERENCES DATA STORAGE =================
const preferences = {
  preferredDays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  preferredTimesByDay: {
    'Mon': [],
    'Tue': [],
    'Wed': [],
    'Thu': [],
    'Fri': [],
    'Sat': []
  },
  preferredUnits: 15, // Default to 15 units
  uploadedFile: null
};

// ================= DAY SELECTION =================
function initializeDayCheckboxes() {
  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const checkboxes = document.querySelectorAll('#filter-panel .days-container input[type="checkbox"]');
  
  checkboxes.forEach((checkbox, index) => {
    // Add data attribute for day identification
    checkbox.setAttribute('data-day', dayLabels[index]);
    
    // Add click handler
    checkbox.addEventListener('change', function() {
      const day = this.getAttribute('data-day');
      if (this.checked) {
        if (!preferences.preferredDays.includes(day)) {
          preferences.preferredDays.push(day);
        }
      } else {
        preferences.preferredDays = preferences.preferredDays.filter(d => d !== day);
      }
      console.log('Preferred days:', preferences.preferredDays);
    });
    
    // Initialize preferences based on checked state
    if (checkbox.checked) {
      const day = checkbox.getAttribute('data-day');
      if (!preferences.preferredDays.includes(day)) {
        preferences.preferredDays.push(day);
      }
    }
  });
}

// ================= UNITS SELECTOR =================
function initializeUnitsSelector() {
  const unitButtons = document.querySelectorAll('.unit-btn');
  
  // Set default selection (15 units)
  unitButtons.forEach(btn => {
    const units = parseInt(btn.getAttribute('data-units'));
    if (units === preferences.preferredUnits) {
      btn.classList.add('selected');
    }
    
    btn.addEventListener('click', function() {
      // Remove selected class from all buttons
      unitButtons.forEach(b => b.classList.remove('selected'));
      
      // Add selected class to clicked button
      this.classList.add('selected');
      
      // Update preferences
      preferences.preferredUnits = parseInt(this.getAttribute('data-units'));
      console.log('Preferred units:', preferences.preferredUnits);
    });
  });
}

// ================= CALENDAR TIME PICKER =================
function initializeCalendarTimePicker() {
  const dayTabs = document.querySelectorAll('.day-tab');
  const timeSlotsContainers = document.querySelectorAll('.time-slots');
  let currentDay = 'Mon';
  
  // Day tab switching
  dayTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const day = this.getAttribute('data-day');
      currentDay = day;
      
      // Update active tab
      dayTabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      
      // Show/hide time slots
      timeSlotsContainers.forEach(container => {
        if (container.getAttribute('data-day') === day) {
          container.style.display = 'grid';
        } else {
          container.style.display = 'none';
        }
      });
    });
  });
  
  // Time slot selection
  const timeSlotButtons = document.querySelectorAll('.time-slot-btn');
  timeSlotButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const time = this.getAttribute('data-time');
      const container = this.closest('.time-slots');
      const day = container.getAttribute('data-day');
      
      // Toggle selection
      if (this.classList.contains('selected')) {
        this.classList.remove('selected');
        preferences.preferredTimesByDay[day] = preferences.preferredTimesByDay[day].filter(t => t !== time);
      } else {
        this.classList.add('selected');
        if (!preferences.preferredTimesByDay[day].includes(time)) {
          preferences.preferredTimesByDay[day].push(time);
        }
      }
      
      console.log('Preferred times by day:', preferences.preferredTimesByDay);
    });
  });
}

// ================= FILE UPLOAD =================
function initializeFileUpload() {
  const fileInput = document.getElementById('tda-file');
  
  if (fileInput) {
    fileInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      
      if (file) {
        if (file.type === 'application/pdf') {
          preferences.uploadedFile = file;
          console.log('File uploaded:', file.name);
          
          // Update UI to show file is selected
          const uploadPanel = document.getElementById('upload-panel');
          const existingMessage = uploadPanel.querySelector('.file-status');
          if (existingMessage) {
            existingMessage.remove();
          }
          
          const statusMessage = document.createElement('p');
          statusMessage.className = 'file-status';
          statusMessage.style.color = '#00274C';
          statusMessage.style.marginTop = '10px';
          statusMessage.textContent = `✓ ${file.name} selected`;
          uploadPanel.appendChild(statusMessage);
        } else {
          alert('Please upload a PDF file.');
          fileInput.value = '';
        }
      }
    });
  }
}

// ================= GENERATE SCHEDULE BUTTON =================
async function initializeGenerateButton() {
  const generateButton = document.querySelector('#upload-panel button');
  
  if (generateButton) {
    generateButton.addEventListener('click', async function() {
      // Check if file is uploaded
      if (!preferences.uploadedFile) {
        alert('Please upload your Titan Degree Audit PDF first.');
        return;
      }
      
      // Check if preferences are set
      if (preferences.preferredDays.length === 0) {
        alert('Please select at least one preferred day.');
        return;
      }
      
      // Disable button and show loading state
      generateButton.disabled = true;
      const originalText = generateButton.textContent;
      generateButton.textContent = 'Generating Schedule...';
      
      try {
        console.log('Starting schedule generation...');
        console.log('API Base URL:', API_BASE_URL);
        console.log('File name:', preferences.uploadedFile.name);
        console.log('File size:', preferences.uploadedFile.size, 'bytes');
        console.log('Preferred units:', preferences.preferredUnits);
        
        // Test API connectivity first
        try {
          const testResponse = await fetch(`${API_BASE_URL}/`, { method: 'GET' });
          console.log('API connectivity test:', testResponse.status);
        } catch (testError) {
          console.warn('API connectivity test failed:', testError);
          throw new Error(`Cannot reach backend server at ${API_BASE_URL}. Please check if the server is running.`);
        }
        
        // Step 1: Upload and parse the PDF
        console.log('Step 1: Uploading PDF...');
        const formData = new FormData();
        formData.append('file', preferences.uploadedFile);
        
        const uploadResponse = await fetch(`${API_BASE_URL}/tda/upload`, {
          method: 'POST',
          body: formData
        });
        
        console.log('Upload response status:', uploadResponse.status);
        
        if (!uploadResponse.ok) {
          let errorMessage = 'Failed to upload and parse PDF';
          try {
            const errorData = await uploadResponse.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
            console.error('Upload error details:', errorData);
          } catch (e) {
            const errorText = await uploadResponse.text();
            console.error('Upload error text:', errorText);
            errorMessage = `HTTP ${uploadResponse.status}: ${errorText}`;
          }
          throw new Error(errorMessage);
        }
        
        const uploadData = await uploadResponse.json();
        console.log('Upload response data:', uploadData);
        const parsedData = uploadData.parsed_data;
        
        if (!parsedData) {
          throw new Error('No parsed data received from server');
        }
        
        // Step 2: Extract completed courses from parsed data
        // Format: course_id should be like "CPSC 131" (subject + number)
        console.log('Step 2: Extracting completed courses...');
        const completedCourses = [];
        if (parsedData.completed_courses && Array.isArray(parsedData.completed_courses)) {
          parsedData.completed_courses.forEach(course => {
            if (course.status === 'completed' && course.subject && course.number) {
              // Format as "SUBJECT NUMBER" (e.g., "CPSC 131")
              const courseId = `${course.subject} ${course.number}`.trim();
              completedCourses.push(courseId);
            }
          });
        }
        
        console.log('Completed courses extracted:', completedCourses);
        
        if (completedCourses.length === 0) {
          console.warn('No completed courses found in parsed data');
        }
        
        // Step 3: Generate schedule with completed courses and preferences
        console.log('Step 3: Generating schedule...');
        const schedulePayload = {
          completed: completedCourses,
          max_units: preferences.preferredUnits
        };
        console.log('Schedule payload:', schedulePayload);
        
        const scheduleResponse = await fetch(`${API_BASE_URL}/schedule/next-semester`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(schedulePayload)
        });
        
        console.log('Schedule response status:', scheduleResponse.status);
        
        if (!scheduleResponse.ok) {
          let errorMessage = 'Failed to generate schedule';
          try {
            const errorData = await scheduleResponse.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
            console.error('Schedule error details:', errorData);
          } catch (e) {
            const errorText = await scheduleResponse.text();
            console.error('Schedule error text:', errorText);
            errorMessage = `HTTP ${scheduleResponse.status}: ${errorText}`;
          }
          throw new Error(errorMessage);
        }
        
        const scheduleData = await scheduleResponse.json();
        console.log('Schedule response data:', scheduleData);
        const schedule = scheduleData.data;
        
        if (!schedule) {
          throw new Error('No schedule data received from server');
        }
        
        // Step 4: Display results
        console.log('Step 4: Displaying results...');
        displayScheduleResults(schedule, parsedData);
        
        // Navigate to results page
        showPage('step-results');
        console.log('Schedule generation completed successfully!');
        
      } catch (error) {
        console.error('Error generating schedule:', error);
        console.error('Error stack:', error.stack);
        alert('Error generating schedule: ' + error.message + '\n\nCheck the browser console for more details.');
      } finally {
        // Re-enable button
        generateButton.disabled = false;
        generateButton.textContent = originalText;
      }
    });
  }
}

// ================= RESULTS PAGE =================
function displayScheduleResults(schedule, parsedData) {
  const schedulePanel = document.getElementById('schedule-panel');
  const openClassesPanel = document.getElementById('open-classes-panel');
  
  // Clear existing content
  schedulePanel.innerHTML = '<h2>Generated Schedule</h2>';
  openClassesPanel.innerHTML = '<h2>Open Classes</h2>';
  
  // Display generated schedule
  if (schedule.planned_courses && schedule.planned_courses.length > 0) {
    const scheduleList = document.createElement('div');
    scheduleList.className = 'schedule-list';
    
    schedule.planned_courses.forEach(course => {
      const courseItem = document.createElement('div');
      courseItem.className = 'course-item';
      courseItem.style.marginBottom = '15px';
      courseItem.style.padding = '10px';
      courseItem.style.border = '1px solid #ccc';
      courseItem.style.borderRadius = '5px';
      
      const courseId = document.createElement('strong');
      courseId.textContent = course.course_id;
      courseId.style.display = 'block';
      courseId.style.marginBottom = '5px';
      
      const courseTitle = document.createElement('span');
      courseTitle.textContent = course.title || 'No title available';
      courseTitle.style.display = 'block';
      courseTitle.style.color = '#666';
      courseTitle.style.marginBottom = '5px';
      
      const courseUnits = document.createElement('span');
      courseUnits.textContent = `${course.units} units`;
      courseUnits.style.display = 'block';
      courseUnits.style.color = '#666';
      courseUnits.style.marginBottom = '5px';
      
      if (course.meeting) {
        const meetingInfo = document.createElement('span');
        meetingInfo.textContent = `${course.meeting.days.join(', ')} ${course.meeting.time}`;
        meetingInfo.style.display = 'block';
        meetingInfo.style.color = '#00274C';
        meetingInfo.style.fontWeight = 'bold';
        courseItem.appendChild(meetingInfo);
      }
      
      courseItem.appendChild(courseId);
      courseItem.appendChild(courseTitle);
      courseItem.appendChild(courseUnits);
      scheduleList.appendChild(courseItem);
    });
    
    const totalUnits = document.createElement('p');
    totalUnits.style.marginTop = '15px';
    totalUnits.style.fontWeight = 'bold';
    totalUnits.textContent = `Total Units: ${schedule.planned_units || 0}`;
    scheduleList.appendChild(totalUnits);
    
    schedulePanel.appendChild(scheduleList);
  } else {
    const noCourses = document.createElement('p');
    noCourses.textContent = 'No courses scheduled. All requirements may be completed or no courses match your preferences.';
    noCourses.style.color = '#666';
    schedulePanel.appendChild(noCourses);
  }
  
  // Display remaining needed courses if available
  if (schedule.remaining_needed && schedule.remaining_needed.length > 0) {
    const remainingDiv = document.createElement('div');
    remainingDiv.style.marginTop = '20px';
    remainingDiv.style.padding = '10px';
    remainingDiv.style.backgroundColor = '#f5f5f5';
    remainingDiv.style.borderRadius = '5px';
    
    const remainingTitle = document.createElement('h3');
    remainingTitle.textContent = 'Remaining Courses Needed';
    remainingTitle.style.marginTop = '0';
    remainingDiv.appendChild(remainingTitle);
    
    const remainingList = document.createElement('ul');
    schedule.remaining_needed.forEach(courseId => {
      const listItem = document.createElement('li');
      listItem.textContent = courseId;
      remainingList.appendChild(listItem);
    });
    remainingDiv.appendChild(remainingList);
    schedulePanel.appendChild(remainingDiv);
  }
  
  // Display parsed TDA info in open classes panel
  if (parsedData && parsedData.completed_courses) {
    const completedCount = parsedData.completed_courses.filter(c => c.status === 'completed').length;
    const infoText = document.createElement('p');
    infoText.textContent = `Parsed ${completedCount} completed course(s) from your TDA.`;
    infoText.style.color = '#666';
    openClassesPanel.appendChild(infoText);
  }
}

function initializeResultsPage() {
  // This will be populated when schedule is generated
  // For now, it's ready for backend integration
}

// ================= INITIALIZE ON PAGE LOAD =================
document.addEventListener('DOMContentLoaded', function() {
  initializeDayCheckboxes();
  initializeCalendarTimePicker();
  initializeUnitsSelector();
  initializeFileUpload();
  initializeGenerateButton();
  initializeResultsPage();
  
  console.log('Titan Scheduler initialized');
});

