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
// Store current schedule data for drag and drop
let currentScheduleData = {
  planned_courses: [],
  planned_units: 0,
  remaining_needed: []
};

async function displayScheduleResults(schedule, parsedData) {
  const schedulePanel = document.getElementById('schedule-panel');
  const openClassesPanel = document.getElementById('open-classes-panel');
  
  // Store schedule data
  currentScheduleData = {
    planned_courses: [...(schedule.planned_courses || [])],
    planned_units: schedule.planned_units || 0,
    remaining_needed: [...(schedule.remaining_needed || [])]
  };
  
  // Clear existing content
  schedulePanel.innerHTML = '<h2>Generated Schedule</h2>';
  openClassesPanel.innerHTML = '<h2>Open Classes</h2>';
  
  // Make schedule panel a drop zone
  schedulePanel.setAttribute('droppable', 'true');
  schedulePanel.addEventListener('dragover', handleDragOver);
  schedulePanel.addEventListener('dragleave', handleDragLeave);
  schedulePanel.addEventListener('drop', handleDrop);
  
  // Display generated schedule
  renderSchedule();
  
  // Fetch and display open classes for remaining needed courses
  if (schedule.remaining_needed && schedule.remaining_needed.length > 0) {
    await fetchAndDisplayOpenClasses(schedule.remaining_needed, openClassesPanel);
  } else {
    const noClasses = document.createElement('p');
    noClasses.textContent = 'No remaining courses needed.';
    noClasses.style.color = '#666';
    openClassesPanel.appendChild(noClasses);
  }
}

function renderSchedule() {
  const schedulePanel = document.getElementById('schedule-panel');
    const scheduleList = document.createElement('div');
    scheduleList.className = 'schedule-list';
  scheduleList.id = 'schedule-list';
    
  if (currentScheduleData.planned_courses && currentScheduleData.planned_courses.length > 0) {
    currentScheduleData.planned_courses.forEach(course => {
      const courseItem = document.createElement('div');
      courseItem.className = 'course-item';
      courseItem.style.marginBottom = '15px';
      courseItem.style.padding = '10px';
      courseItem.style.border = '1px solid #ccc';
      courseItem.style.borderRadius = '5px';
      courseItem.style.backgroundColor = '#ffffff';
      
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
    totalUnits.id = 'total-units';
    totalUnits.style.marginTop = '15px';
    totalUnits.style.fontWeight = 'bold';
    totalUnits.textContent = `Total Units: ${currentScheduleData.planned_units || 0}`;
    scheduleList.appendChild(totalUnits);
    
    schedulePanel.appendChild(scheduleList);
  } else {
    const noCourses = document.createElement('p');
    noCourses.textContent = 'No courses scheduled. Drag classes from the Open Classes list to add them.';
    noCourses.style.color = '#666';
    scheduleList.appendChild(noCourses);
    schedulePanel.appendChild(scheduleList);
  }
}

async function fetchAndDisplayOpenClasses(remainingNeeded, openClassesPanel) {
  try {
    // Fetch open classes for each remaining needed course
    const openClassesPromises = remainingNeeded.map(async (courseId) => {
      // Extract subject and number from courseId (e.g., "CPSC 131" -> subject="CPSC", course="131")
      const parts = courseId.trim().split(/\s+/);
      if (parts.length < 2) return [];
      
      const subject = parts[0];
      const course = parts.slice(1).join(' ');
      
      try {
        const response = await fetch(`${API_BASE_URL}/open/query?subject=${encodeURIComponent(subject)}&course=${encodeURIComponent(course)}&only_open=true`);
        if (!response.ok) {
          console.warn(`Failed to fetch open classes for ${courseId}`);
          return [];
        }
        const data = await response.json();
        return Array.isArray(data) ? data : [];
      } catch (error) {
        console.error(`Error fetching open classes for ${courseId}:`, error);
        return [];
      }
    });
    
    const allOpenClasses = await Promise.all(openClassesPromises);
    const flattenedClasses = allOpenClasses.flat();
    
    if (flattenedClasses.length === 0) {
      const noClasses = document.createElement('p');
      noClasses.textContent = 'No open classes found for remaining needed courses.';
      noClasses.style.color = '#666';
      openClassesPanel.appendChild(noClasses);
      return;
    }
    
    // Group by course_id
    const classesByCourse = {};
    flattenedClasses.forEach(classItem => {
      const courseId = classItem.course_id || `${classItem.subject} ${classItem.number}`;
      if (!classesByCourse[courseId]) {
        classesByCourse[courseId] = [];
      }
      classesByCourse[courseId].push(classItem);
    });
    
    // Display open classes
    const classesList = document.createElement('div');
    classesList.className = 'open-classes-list';
    
    Object.keys(classesByCourse).forEach(courseId => {
      const courseGroup = classesByCourse[courseId];
      courseGroup.forEach(classItem => {
        const classCard = document.createElement('div');
        classCard.className = 'open-class-item';
        classCard.draggable = true;
        classCard.style.marginBottom = '10px';
        classCard.style.padding = '12px';
        classCard.style.border = '2px solid #00274C';
        classCard.style.borderRadius = '8px';
        classCard.style.backgroundColor = '#ffffff';
        classCard.style.cursor = 'grab';
        classCard.style.transition = 'all 0.2s ease';
        
        // Store course data for drag and drop
        classCard.dataset.courseId = classItem.course_id || `${classItem.subject} ${classItem.number}`;
        classCard.dataset.courseTitle = classItem.title || classItem.description || '';
        classCard.dataset.courseUnits = classItem.units || 3;
        classCard.dataset.crn = classItem.crn;
        classCard.dataset.term = classItem.term;
        
        // Store meeting info as JSON string
        if (classItem.meetings && classItem.meetings.length > 0) {
          classCard.dataset.meetings = JSON.stringify(classItem.meetings);
        }
        
        // Add hover effect
        classCard.addEventListener('mouseenter', () => {
          classCard.style.transform = 'translateY(-2px)';
          classCard.style.boxShadow = '0 4px 8px rgba(0, 39, 76, 0.2)';
        });
        classCard.addEventListener('mouseleave', () => {
          classCard.style.transform = 'translateY(0)';
          classCard.style.boxShadow = 'none';
        });
        
        // Course ID
        const courseIdEl = document.createElement('strong');
        courseIdEl.textContent = classCard.dataset.courseId;
        courseIdEl.style.display = 'block';
        courseIdEl.style.marginBottom = '5px';
        courseIdEl.style.color = '#00274C';
        
        // Title
        const titleEl = document.createElement('span');
        titleEl.textContent = classItem.title || classItem.description || 'No title available';
        titleEl.style.display = 'block';
        titleEl.style.color = '#666';
        titleEl.style.fontSize = '14px';
        titleEl.style.marginBottom = '5px';
        
        // Units
        const unitsEl = document.createElement('span');
        unitsEl.textContent = `${classItem.units || 3} units`;
        unitsEl.style.display = 'block';
        unitsEl.style.color = '#666';
        unitsEl.style.fontSize = '13px';
        unitsEl.style.marginBottom = '5px';
        
        // Meeting info
        if (classItem.meetings && classItem.meetings.length > 0) {
          const meetingsInfo = classItem.meetings.map(meeting => {
            const day = meeting.day || '';
            let time = '';
            
            // Convert start/end from minutes to time format
            if (meeting.start !== undefined && meeting.end !== undefined) {
              const startHours = Math.floor(meeting.start / 60);
              const startMins = meeting.start % 60;
              const endHours = Math.floor(meeting.end / 60);
              const endMins = meeting.end % 60;
              
              const formatTime = (hours, mins) => {
                const period = hours >= 12 ? 'PM' : 'AM';
                const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
                return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
              };
              
              time = `${formatTime(startHours, startMins)}-${formatTime(endHours, endMins)}`;
            } else if (meeting.time) {
              time = meeting.time;
            }
            
            return `${day} ${time}`.trim();
          }).filter(Boolean).join('; ');
          
          if (meetingsInfo) {
            const meetingEl = document.createElement('span');
            meetingEl.textContent = meetingsInfo;
            meetingEl.style.display = 'block';
            meetingEl.style.color = '#00274C';
            meetingEl.style.fontSize = '12px';
            meetingEl.style.fontWeight = 'bold';
            meetingEl.style.marginTop = '5px';
            classCard.appendChild(meetingEl);
          }
        }
        
        classCard.appendChild(courseIdEl);
        classCard.appendChild(titleEl);
        classCard.appendChild(unitsEl);
        
        // Drag event handlers
        classCard.addEventListener('dragstart', handleDragStart);
        classCard.addEventListener('dragend', handleDragEnd);
        
        classesList.appendChild(classCard);
      });
    });
    
    openClassesPanel.appendChild(classesList);
    
  } catch (error) {
    console.error('Error fetching open classes:', error);
    const errorMsg = document.createElement('p');
    errorMsg.textContent = 'Error loading open classes. Please try again.';
    errorMsg.style.color = '#d32f2f';
    openClassesPanel.appendChild(errorMsg);
  }
}

// Drag and drop handlers
let draggedElement = null;

function handleDragStart(e) {
  draggedElement = e.target;
  e.target.style.opacity = '0.5';
  e.target.style.cursor = 'grabbing';
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', e.target.outerHTML);
}

function handleDragEnd(e) {
  e.target.style.opacity = '1';
  e.target.style.cursor = 'grab';
  draggedElement = null;
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.dataTransfer.dropEffect = 'move';
  const schedulePanel = e.currentTarget;
  schedulePanel.style.border = '2px dashed #00274C';
  schedulePanel.style.backgroundColor = '#f0f7ff';
  return false;
}

function handleDragLeave(e) {
  const schedulePanel = e.currentTarget;
  // Only reset if we're actually leaving the panel (not just moving to a child)
  if (!schedulePanel.contains(e.relatedTarget)) {
    schedulePanel.style.border = 'none';
    schedulePanel.style.backgroundColor = '#ffffff';
  }
}

function handleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }
  
  e.preventDefault();
  const schedulePanel = e.currentTarget;
  schedulePanel.style.border = 'none';
  schedulePanel.style.backgroundColor = '#ffffff';
  
  if (!draggedElement) return;
  
  // Get course data from dragged element
  const courseId = draggedElement.dataset.courseId;
  const courseTitle = draggedElement.dataset.courseTitle;
  const courseUnits = parseInt(draggedElement.dataset.courseUnits) || 3;
  
  // Check if course is already in schedule
  const alreadyAdded = currentScheduleData.planned_courses.some(
    c => c.course_id === courseId
  );
  
  if (alreadyAdded) {
    alert(`${courseId} is already in your schedule.`);
    return;
  }
  
  // Add course to schedule
  const newCourse = {
    course_id: courseId,
    title: courseTitle,
    units: courseUnits,
    meeting: {
      days: [],
      time: 'TBA'
    }
  };
  
  // Extract meeting info from stored dataset
  if (draggedElement.dataset.meetings) {
    try {
      const meetings = JSON.parse(draggedElement.dataset.meetings);
      if (meetings && meetings.length > 0) {
        const firstMeeting = meetings[0];
        
        // Handle day - can be string or array
        if (firstMeeting.day) {
          newCourse.meeting.days = [firstMeeting.day];
        } else if (firstMeeting.days && Array.isArray(firstMeeting.days)) {
          newCourse.meeting.days = firstMeeting.days;
        }
        
        // Handle time - convert from minutes if needed
        if (firstMeeting.time) {
          newCourse.meeting.time = firstMeeting.time;
        } else if (firstMeeting.start !== undefined && firstMeeting.end !== undefined) {
          const startHours = Math.floor(firstMeeting.start / 60);
          const startMins = firstMeeting.start % 60;
          const endHours = Math.floor(firstMeeting.end / 60);
          const endMins = firstMeeting.end % 60;
          
          const formatTime = (hours, mins) => {
            const period = hours >= 12 ? 'PM' : 'AM';
            const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
            return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
          };
          
          newCourse.meeting.time = `${formatTime(startHours, startMins)}-${formatTime(endHours, endMins)}`;
        } else {
          newCourse.meeting.time = 'TBA';
        }
      }
    } catch (e) {
      console.warn('Error parsing meeting data:', e);
    }
  }
  
  currentScheduleData.planned_courses.push(newCourse);
  currentScheduleData.planned_units += courseUnits;
  
  // Remove from remaining needed if it's there
  currentScheduleData.remaining_needed = currentScheduleData.remaining_needed.filter(
    c => c !== courseId
  );
  
  // Re-render schedule
  const schedulePanel = document.getElementById('schedule-panel');
  const scheduleList = document.getElementById('schedule-list');
  if (scheduleList) {
    scheduleList.remove();
  }
  renderSchedule();
  
  // Remove dragged element from open classes (optional - you might want to keep it)
  // draggedElement.remove();
  
  return false;
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

