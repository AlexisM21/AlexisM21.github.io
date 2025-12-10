// script.js

// ================= API CONFIGURATION =================
// Change this to match your backend server URL
const API_BASE_URL = 'http://titanbackend.online';

// ================= PAGE NAVIGATION =================
function showPage(pageId) {
  const pages = document.querySelectorAll(".page");
  pages.forEach(page => {
    page.classList.toggle("active", page.id === pageId);
  });
}

function initializeNavigation() {
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
}

// ================= LOADING OVERLAY =================
function showLoadingOverlay() {
  // Remove existing overlay if any
  const existing = document.getElementById('loading-overlay');
  if (existing) {
    existing.remove();
  }
  
  const overlay = document.createElement('div');
  overlay.id = 'loading-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100%';
  overlay.style.height = '100%';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
  overlay.style.display = 'flex';
  overlay.style.justifyContent = 'center';
  overlay.style.alignItems = 'center';
  overlay.style.zIndex = '9999';
  overlay.style.flexDirection = 'column';
  
  const spinner = document.createElement('div');
  spinner.className = 'loading-spinner';
  spinner.style.width = '50px';
  spinner.style.height = '50px';
  spinner.style.border = '5px solid #f3f3f3';
  spinner.style.borderTop = '5px solid #00274C';
  spinner.style.borderRadius = '50%';
  spinner.style.animation = 'spin 1s linear infinite';
  
  const text = document.createElement('p');
  text.textContent = 'Generating your schedule...';
  text.style.color = 'white';
  text.style.fontSize = '18px';
  text.style.marginTop = '20px';
  text.style.fontWeight = '600';
  
  overlay.appendChild(spinner);
  overlay.appendChild(text);
  document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.remove();
  }
}

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
      
      // Show loading overlay
      showLoadingOverlay();
      
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
        
        // Backend returns only open classes in format: { "Open Classes:": { "eligible_classes": [...] } }
        const openClassesData = uploadData["Open Classes:"];
        
        if (!openClassesData || !openClassesData.eligible_classes) {
          throw new Error('No open classes received from server');
        }
        
        const eligibleClasses = openClassesData.eligible_classes || [];
        console.log(`Received ${eligibleClasses.length} eligible open classes`);
        
        // Step 2: Generate schedule from eligible classes with filters
        console.log('Step 2: Generating schedule with filters...');
        const generatedSchedule = generateScheduleFromClasses(eligibleClasses, preferences);
        console.log('Generated schedule:', generatedSchedule);
        
        // Step 3: Display the generated schedule and remaining open classes
        console.log('Step 3: Displaying schedule and open classes...');
        displayScheduleFromUpload(eligibleClasses, generatedSchedule);
        
        // Navigate to results page
        showPage('step-results');
        console.log('Schedule generation completed successfully!');
        
      } catch (error) {
        console.error('Error generating schedule:', error);
        console.error('Error stack:', error.stack);
        alert('Error generating schedule: ' + error.message + '\n\nCheck the browser console for more details.');
      } finally {
        // Hide loading overlay
        hideLoadingOverlay();
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
  
  // Make open classes panel a drop zone for removing schedule items
  openClassesPanel.setAttribute('droppable', 'true');
  openClassesPanel.addEventListener('dragover', (e) => {
    // Only show drop zone if dragging from schedule
    if (draggedFromSchedule) {
      handleDragOver(e);
    }
  });
  openClassesPanel.addEventListener('dragleave', handleDragLeave);
  openClassesPanel.addEventListener('drop', handleScheduleDrop);
  
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
  
  // Remove existing schedule list if it exists
  const existingList = document.getElementById('schedule-list');
  if (existingList) {
    existingList.remove();
  }
  
  const scheduleList = document.createElement('div');
  scheduleList.className = 'schedule-list';
  scheduleList.id = 'schedule-list';
    
  if (currentScheduleData.planned_courses && currentScheduleData.planned_courses.length > 0) {
    currentScheduleData.planned_courses.forEach((course, index) => {
      const courseItem = document.createElement('div');
      courseItem.className = 'course-item';
      courseItem.draggable = true;
      courseItem.style.marginBottom = '15px';
      courseItem.style.padding = '10px';
      courseItem.style.border = '1px solid #ccc';
      courseItem.style.borderRadius = '5px';
      courseItem.style.backgroundColor = '#ffffff';
      courseItem.style.cursor = 'grab';
      courseItem.style.transition = 'all 0.2s ease';
      
      // Store course data for drag and drop
      courseItem.dataset.courseIndex = index;
      courseItem.dataset.courseId = course.course_id;
      courseItem.dataset.courseTitle = course.title || '';
      courseItem.dataset.courseUnits = course.units || 3;
      if (course.meeting) {
        courseItem.dataset.meetingDays = JSON.stringify(course.meeting.days || []);
        courseItem.dataset.meetingTime = course.meeting.time || 'TBA';
      }
      
      // Add hover effect
      courseItem.addEventListener('mouseenter', () => {
        courseItem.style.transform = 'translateY(-2px)';
        courseItem.style.boxShadow = '0 4px 8px rgba(0, 39, 76, 0.2)';
      });
      courseItem.addEventListener('mouseleave', () => {
        courseItem.style.transform = 'translateY(0)';
        courseItem.style.boxShadow = 'none';
      });
      
      const courseId = document.createElement('strong');
      const sectionText = course.section ? ` - Section ${course.section}` : '';
      courseId.textContent = `${course.course_id}${sectionText}`;
      courseId.style.display = 'block';
      courseId.style.marginBottom = '5px';
      courseId.style.color = '#00274C';
      
      const courseTitle = document.createElement('span');
      courseTitle.textContent = course.title || 'No title available';
      courseTitle.style.display = 'block';
      courseTitle.style.color = '#666';
      courseTitle.style.marginBottom = '5px';
      courseTitle.style.fontSize = '14px';
      
      // Professor info
      if (course.professor) {
        const professorEl = document.createElement('span');
        professorEl.textContent = `Professor: ${course.professor}`;
        professorEl.style.display = 'block';
        professorEl.style.color = '#666';
        professorEl.style.fontSize = '13px';
        professorEl.style.marginBottom = '5px';
        courseItem.appendChild(professorEl);
      }
      
      const courseUnits = document.createElement('span');
      courseUnits.textContent = `${course.units} units`;
      courseUnits.style.display = 'block';
      courseUnits.style.color = '#666';
      courseUnits.style.fontSize = '13px';
      courseUnits.style.marginBottom = '5px';
      
      // CRN if available
      if (course.crn) {
        const crnEl = document.createElement('span');
        crnEl.textContent = `CRN: ${course.crn}`;
        crnEl.style.display = 'block';
        crnEl.style.color = '#666';
        crnEl.style.fontSize = '12px';
        crnEl.style.marginBottom = '5px';
        courseItem.appendChild(crnEl);
      }
      
      if (course.meeting) {
        const meetingInfo = document.createElement('span');
        const daysText = course.meeting.days && course.meeting.days.length > 0
          ? course.meeting.days.join(', ')
          : 'TBA';
        meetingInfo.textContent = `${daysText} ${course.meeting.time || 'TBA'}`;
        meetingInfo.style.display = 'block';
        meetingInfo.style.color = '#00274C';
        meetingInfo.style.fontWeight = 'bold';
        meetingInfo.style.fontSize = '13px';
        meetingInfo.style.marginTop = '5px';
        courseItem.appendChild(meetingInfo);
      }
      
      courseItem.appendChild(courseId);
      courseItem.appendChild(courseTitle);
      courseItem.appendChild(courseUnits);
      
      // Add drag event handlers
      courseItem.addEventListener('dragstart', handleScheduleDragStart);
      courseItem.addEventListener('dragend', handleScheduleDragEnd);
      
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

// ================= PROFESSOR RATING FETCH =================
async function fetchProfessorRating(professorName, professorElement) {
  if (!professorName || !professorName.trim()) {
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/professor/rating?professor_name=${encodeURIComponent(professorName)}`);
    
    if (!response.ok) {
      // Silently fail - don't show error if rating service is unavailable
      if (response.status === 503) {
        console.log(`Rate My Professor service unavailable for ${professorName}`);
      }
      return;
    }
    
    const data = await response.json();
    
    if (data.found && data.overall_rating) {
      const rating = parseFloat(data.overall_rating);
      const numRatings = data.num_ratings || 0;
      
      // Determine rating color
      let ratingColor = '#666';
      if (rating >= 4.0) {
        ratingColor = '#2e7d32'; // Green for good ratings
      } else if (rating >= 3.0) {
        ratingColor = '#f57c00'; // Orange for average ratings
      } else if (rating > 0) {
        ratingColor = '#d32f2f'; // Red for poor ratings
      }
      
      // Update professor element with rating
      const ratingText = numRatings > 0 
        ? `Professor: ${professorName} | RMP Rating: ${rating.toFixed(1)}/5.0 (${numRatings} reviews)`
        : `Professor: ${professorName} | RMP Rating: ${rating.toFixed(1)}/5.0`;
      
      professorElement.textContent = ratingText;
      professorElement.style.color = ratingColor;
      professorElement.style.fontWeight = '500';
      
      // Add a small star icon or emoji
      const starSpan = document.createElement('span');
      starSpan.textContent = ' ⭐';
      starSpan.style.marginLeft = '3px';
      professorElement.appendChild(starSpan);
    } else {
      // Professor not found on Rate My Professor
      professorElement.textContent = `Professor: ${professorName} | RMP Rating: Not found`;
      professorElement.style.color = '#999';
    }
  } catch (error) {
    // Silently fail - don't disrupt the UI if rating fetch fails
    console.log(`Error fetching rating for ${professorName}:`, error);
  }
}

// ================= SCHEDULE GENERATION =================
function generateScheduleFromClasses(eligibleClasses, preferences) {
  const maxUnits = preferences.preferredUnits || 15;
  const preferredDays = preferences.preferredDays || [];
  const preferredTimesByDay = preferences.preferredTimesByDay || {};
  
  // Helper to normalize day names
  function normalizeDay(day) {
    if (typeof day === 'number') {
      const dayMap = { 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun' };
      return dayMap[day] || day.toString();
    }
    if (typeof day === 'string') {
      const dayLower = day.toLowerCase();
      const dayMap = {
        'monday': 'Mon', 'mon': 'Mon',
        'tuesday': 'Tue', 'tue': 'Tue',
        'wednesday': 'Wed', 'wed': 'Wed',
        'thursday': 'Thu', 'thu': 'Thu',
        'friday': 'Fri', 'fri': 'Fri',
        'saturday': 'Sat', 'sat': 'Sat',
        'sunday': 'Sun', 'sun': 'Sun'
      };
      return dayMap[dayLower] || day;
    }
    return day;
  }
  
  // Helper to check if a meeting matches preferred days
  function matchesPreferredDays(meetings) {
    if (!meetings || meetings.length === 0) return true; // TBA classes are allowed
    if (preferredDays.length === 0) return true; // No day filter
    
    const meetingDays = new Set();
    meetings.forEach(meeting => {
      if (meeting.day) {
        meetingDays.add(normalizeDay(meeting.day));
      } else if (meeting.days && Array.isArray(meeting.days)) {
        meeting.days.forEach(d => meetingDays.add(normalizeDay(d)));
      } else if (meeting.day_of_week) {
        meetingDays.add(normalizeDay(meeting.day_of_week));
      }
    });
    
    // Normalize preferred days
    const normalizedPreferred = preferredDays.map(d => normalizeDay(d));
    
    // Check if any meeting day is in preferred days
    return Array.from(meetingDays).some(day => normalizedPreferred.includes(day));
  }
  
  // Helper to check if a meeting matches preferred times
  function matchesPreferredTimes(meetings) {
    if (!meetings || meetings.length === 0) return true; // TBA classes are allowed
    
    // If no time preferences set for any day, allow all times
    const hasTimePreferences = Object.values(preferredTimesByDay).some(times => times.length > 0);
    if (!hasTimePreferences) return true;
    
    return meetings.some(meeting => {
      const meetingDay = meeting.day || (meeting.days && meeting.days[0]);
      if (!meetingDay) return true; // TBA
      
      const preferredTimes = preferredTimesByDay[meetingDay] || [];
      if (preferredTimes.length === 0) return true; // No time filter for this day
      
      // Check if meeting time overlaps with preferred times
      let meetingStart = null;
      let meetingEnd = null;
      
      if (meeting.start !== undefined && meeting.end !== undefined) {
        meetingStart = meeting.start;
        meetingEnd = meeting.end;
      } else if (meeting.time) {
        // Parse time string like "8:00 AM-9:00 AM" or "08:00-09:00"
        const timeMatch = meeting.time.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/);
        if (timeMatch) {
          let hours = parseInt(timeMatch[1]);
          const mins = parseInt(timeMatch[2]);
          const period = timeMatch[3];
          if (period === 'PM' && hours !== 12) hours += 12;
          if (period === 'AM' && hours === 12) hours = 0;
          meetingStart = hours * 60 + mins;
          meetingEnd = meetingStart + 60; // Assume 1 hour if end not specified
        }
      }
      
      if (meetingStart === null) return true; // Can't parse time, allow it
      
      // Check if any preferred time overlaps with meeting time
      return preferredTimes.some(prefTime => {
        const [prefHour, prefMin] = prefTime.split(':').map(Number);
        const prefStart = prefHour * 60 + prefMin;
        const prefEnd = prefStart + 60; // Assume 1 hour slots
        
        // Check for overlap
        return !(meetingEnd <= prefStart || meetingStart >= prefEnd);
      });
    });
  }
  
  // Helper to check for time conflicts between courses
  function hasTimeConflict(newCourse, existingCourses) {
    const newMeetings = newCourse.meetings || [];
    if (newMeetings.length === 0) return false; // TBA classes don't conflict
    
    return existingCourses.some(existing => {
      const existingMeetings = existing.meetings || [];
      if (existingMeetings.length === 0) return false;
      
      // Check if any meetings overlap
      return newMeetings.some(newMeeting => {
        const newDay = normalizeDay(newMeeting.day || (newMeeting.days && newMeeting.days[0]) || newMeeting.day_of_week);
        let newStart = newMeeting.start;
        let newEnd = newMeeting.end;
        
        // Handle start_min/end_min format
        if (newStart === undefined && newMeeting.start_min !== undefined) {
          newStart = newMeeting.start_min;
        }
        if (newEnd === undefined && newMeeting.end_min !== undefined) {
          newEnd = newMeeting.end_min;
        }
        
        if (!newDay || newStart === undefined || newEnd === undefined) return false;
        
        return existingMeetings.some(existingMeeting => {
          const existingDay = normalizeDay(existingMeeting.day || (existingMeeting.days && existingMeeting.days[0]) || existingMeeting.day_of_week);
          let existingStart = existingMeeting.start;
          let existingEnd = existingMeeting.end;
          
          // Handle start_min/end_min format
          if (existingStart === undefined && existingMeeting.start_min !== undefined) {
            existingStart = existingMeeting.start_min;
          }
          if (existingEnd === undefined && existingMeeting.end_min !== undefined) {
            existingEnd = existingMeeting.end_min;
          }
          
          if (!existingDay || existingStart === undefined || existingEnd === undefined) return false;
          
          // Same day and overlapping times
          return newDay === existingDay && 
                 !(newEnd <= existingStart || newStart >= existingEnd);
        });
      });
    });
  }
  
  // Filter classes by preferences
  const filteredClasses = eligibleClasses.filter(classItem => {
    const meetings = classItem.meetings || [];
    
    // Check day preference
    if (!matchesPreferredDays(meetings)) return false;
    
    // Check time preference
    if (!matchesPreferredTimes(meetings)) return false;
    
    return true;
  });
  
  // Group by course_id to avoid duplicates
  const classesByCourse = {};
  filteredClasses.forEach(classItem => {
    const courseId = classItem.course_id || `${classItem.subject} ${classItem.number}`;
    if (!classesByCourse[courseId]) {
      classesByCourse[courseId] = [];
    }
    classesByCourse[courseId].push(classItem);
  });
  
  // Helper to extract subject and number from course ID
  function parseCourseId(courseId) {
    // Match patterns like "CPSC 131", "CHEM 122", "MATH 150A", etc.
    const match = courseId.match(/^([A-Z]+)\s+(\d+)([A-Z]*)$/);
    if (match) {
      return {
        subject: match[1],
        number: parseInt(match[2]),
        suffix: match[3] || ''
      };
    }
    return { subject: '', number: 0, suffix: '' };
  }
  
  // Helper to check if two courses are in a sequence (e.g., CHEM 122 and 123)
  // This prevents scheduling courses that are typically prerequisites/corequisites
  function areInSequence(courseId1, courseId2) {
    const course1 = parseCourseId(courseId1);
    const course2 = parseCourseId(courseId2);
    
    // Same subject
    if (course1.subject !== course2.subject) return false;
    
    // If they have the same base number but different suffixes (e.g., 122A and 122B), they're related
    if (course1.number === course2.number && course1.suffix !== course2.suffix && 
        course1.suffix !== '' && course2.suffix !== '') {
      return true;
    }
    
    // Check if numbers are consecutive (e.g., 122/123, 1/2, 10/11)
    // This catches cases like CHEM 122 and CHEM 123
    const numDiff = Math.abs(course1.number - course2.number);
    if (numDiff === 1 && course1.suffix === '' && course2.suffix === '') {
      return true;
    }
    
    // Also check for common sequence patterns (e.g., 1/2, 10/11, 100/101, 120/121, 122/123)
    // where the first digit(s) are the same and last digit differs by 1
    if (course1.number >= 100 && course2.number >= 100) {
      const num1Str = course1.number.toString();
      const num2Str = course2.number.toString();
      // Check if they're like 122/123 (same first digits, last digit differs by 1)
      if (num1Str.length === num2Str.length && num1Str.length >= 3) {
        const prefix1 = num1Str.slice(0, -1);
        const prefix2 = num2Str.slice(0, -1);
        const last1 = parseInt(num1Str.slice(-1));
        const last2 = parseInt(num2Str.slice(-1));
        if (prefix1 === prefix2 && Math.abs(last1 - last2) === 1) {
          return true;
        }
      }
    }
    
    return false;
  }
  
  // Helper to check if a course conflicts with already scheduled courses (sequence conflicts)
  function hasSequenceConflict(newCourseId, existingCourses) {
    return existingCourses.some(existing => {
      const existingCourseId = existing.course_id;
      return areInSequence(newCourseId, existingCourseId);
    });
  }
  
  // Helper to check if course is CS/CPSC
  function isComputerScience(courseId) {
    const parsed = parseCourseId(courseId);
    return parsed.subject === 'CPSC' || parsed.subject === 'CS';
  }
  
  // Generate schedule: select one section per course, avoiding conflicts
  const plannedCourses = [];
  let totalUnits = 0;
  const usedCourseIds = new Set();
  
  // Sort courses: prioritize CS/CPSC classes, then by units
  const sortedCourses = Object.keys(classesByCourse).sort((a, b) => {
    const aIsCS = isComputerScience(a);
    const bIsCS = isComputerScience(b);
    
    // CS classes first
    if (aIsCS && !bIsCS) return -1;
    if (!aIsCS && bIsCS) return 1;
    
    // Then sort by units (prefer smaller units to fit more courses)
    const aUnits = classesByCourse[a][0].units || 3;
    const bUnits = classesByCourse[b][0].units || 3;
    return aUnits - bUnits;
  });
  
  for (const courseId of sortedCourses) {
    if (totalUnits >= maxUnits) break;
    if (usedCourseIds.has(courseId)) continue;
    
    const sections = classesByCourse[courseId];
    
    // Try each section until we find one without conflicts
    for (const section of sections) {
      const courseUnits = section.units || 3;
      
      if (totalUnits + courseUnits > maxUnits) continue;
      
      // Check for time conflicts
      const courseForConflict = {
        meetings: section.meetings || []
      };
      
      if (hasTimeConflict(courseForConflict, plannedCourses)) continue;
      
      // Check for sequence conflicts (e.g., CHEM 122 and 123)
      if (hasSequenceConflict(courseId, plannedCourses)) continue;
      
      // Add to schedule
      const meeting = section.meetings && section.meetings.length > 0 
        ? section.meetings[0] 
        : null;
      
      let meetingDays = [];
      let meetingTime = 'TBA';
      
      if (meeting) {
        // Extract days
        if (meeting.days && Array.isArray(meeting.days)) {
          meetingDays = meeting.days.map(d => normalizeDay(d));
        } else if (meeting.day) {
          meetingDays = [normalizeDay(meeting.day)];
        } else if (meeting.day_of_week) {
          meetingDays = [normalizeDay(meeting.day_of_week)];
        }
        
        // Extract time
        if (meeting.time) {
          meetingTime = meeting.time;
        } else {
          let start = meeting.start;
          let end = meeting.end;
          
          // Handle start_min/end_min format
          if (start === undefined && meeting.start_min !== undefined) {
            start = meeting.start_min;
          }
          if (end === undefined && meeting.end_min !== undefined) {
            end = meeting.end_min;
          }
          
          if (start !== undefined && end !== undefined) {
            meetingTime = formatMeetingTime(start, end);
          }
        }
      }
      
      const plannedCourse = {
        course_id: courseId,
        title: section.title || section.description || '',
        units: courseUnits,
        meeting: {
          days: meetingDays,
          time: meetingTime
        },
        crn: section.crn,
        section: section.section,
        professor: section.professor,
        meetings: section.meetings // Keep full meetings data for conflict checking
      };
      
      plannedCourses.push(plannedCourse);
      totalUnits += courseUnits;
      usedCourseIds.add(courseId);
      break; // Found a section, move to next course
    }
  }
  
  // Get remaining needed courses (courses not in schedule)
  const remainingNeeded = Object.keys(classesByCourse)
    .filter(courseId => !usedCourseIds.has(courseId));
  
  return {
    planned_courses: plannedCourses,
    planned_units: totalUnits,
    remaining_needed: remainingNeeded
  };
}

function formatMeetingTime(startMinutes, endMinutes) {
  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
    return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
  };
  return `${formatTime(startMinutes)}-${formatTime(endMinutes)}`;
}

// ================= DISPLAY SCHEDULE FROM UPLOAD =================
function displayScheduleFromUpload(eligibleClasses, generatedSchedule) {
  const schedulePanel = document.getElementById('schedule-panel');
  const openClassesPanel = document.getElementById('open-classes-panel');
  
  // Store schedule data
  currentScheduleData = {
    planned_courses: [...(generatedSchedule.planned_courses || [])],
    planned_units: generatedSchedule.planned_units || 0,
    remaining_needed: [...(generatedSchedule.remaining_needed || [])]
  };
  
  // Clear existing content
  schedulePanel.innerHTML = '<h2>Generated Schedule</h2>';
  openClassesPanel.innerHTML = '<h2>Open Classes</h2>';
  
  // Make schedule panel a drop zone
  schedulePanel.setAttribute('droppable', 'true');
  schedulePanel.addEventListener('dragover', handleDragOver);
  schedulePanel.addEventListener('dragleave', handleDragLeave);
  schedulePanel.addEventListener('drop', handleDrop);
  
  // Make open classes panel a drop zone for removing schedule items
  openClassesPanel.setAttribute('droppable', 'true');
  openClassesPanel.addEventListener('dragover', (e) => {
    if (draggedFromSchedule) {
      handleDragOver(e);
    }
  });
  openClassesPanel.addEventListener('dragleave', handleDragLeave);
  openClassesPanel.addEventListener('drop', handleScheduleDrop);
  
  // Display generated schedule
  renderSchedule();
  
  // Filter out classes that are already in the schedule
  const scheduledCourseIds = new Set(generatedSchedule.planned_courses.map(c => c.course_id));
  const remainingClasses = eligibleClasses.filter(classItem => {
    const courseId = classItem.course_id || `${classItem.subject} ${classItem.number}`;
    return !scheduledCourseIds.has(courseId);
  });
  
  // Display remaining open classes
  if (remainingClasses && remainingClasses.length > 0) {
    displayOpenClassesList(remainingClasses, openClassesPanel);
  } else {
    const noClasses = document.createElement('p');
    noClasses.textContent = 'No additional open classes available.';
    noClasses.style.color = '#666';
    openClassesPanel.appendChild(noClasses);
  }
}

// ================= DISPLAY OPEN CLASSES FROM UPLOAD =================
function displayOpenClassesFromUpload(eligibleClasses) {
  const schedulePanel = document.getElementById('schedule-panel');
  const openClassesPanel = document.getElementById('open-classes-panel');
  
  // Initialize empty schedule data
  currentScheduleData = {
    planned_courses: [],
    planned_units: 0,
    remaining_needed: []
  };
  
  // Clear existing content
  schedulePanel.innerHTML = '<h2>Generated Schedule</h2>';
  openClassesPanel.innerHTML = '<h2>Open Classes</h2>';
  
  // Make schedule panel a drop zone
  schedulePanel.setAttribute('droppable', 'true');
  schedulePanel.addEventListener('dragover', handleDragOver);
  schedulePanel.addEventListener('dragleave', handleDragLeave);
  schedulePanel.addEventListener('drop', handleDrop);
  
  // Make open classes panel a drop zone for removing schedule items
  openClassesPanel.setAttribute('droppable', 'true');
  openClassesPanel.addEventListener('dragover', (e) => {
    if (draggedFromSchedule) {
      handleDragOver(e);
    }
  });
  openClassesPanel.addEventListener('dragleave', handleDragLeave);
  openClassesPanel.addEventListener('drop', handleScheduleDrop);
  
  // Display empty schedule
  renderSchedule();
  
  // Display open classes directly
  if (eligibleClasses && eligibleClasses.length > 0) {
    displayOpenClassesList(eligibleClasses, openClassesPanel);
  } else {
    const noClasses = document.createElement('p');
    noClasses.textContent = 'No open classes found for courses you need to take.';
    noClasses.style.color = '#666';
    openClassesPanel.appendChild(noClasses);
  }
}

function displayOpenClassesList(classItems, openClassesPanel) {
  // Group by course_id
  const classesByCourse = {};
  classItems.forEach(classItem => {
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
      const classCard = createClassCard(classItem);
      classesList.appendChild(classCard);
    });
  });
  
  openClassesPanel.appendChild(classesList);
}

function createClassCard(classItem) {
  const classCard = document.createElement("div");
  classCard.className = "open-class-item";
  classCard.draggable = true;
  classCard.style.marginBottom = "10px";
  classCard.style.padding = "12px";
  classCard.style.border = "2px solid #00274C";
  classCard.style.borderRadius = "8px";
  classCard.style.backgroundColor = "#ffffff";
  classCard.style.cursor = "grab";
  classCard.style.transition = "all 0.2s ease";

  // Store course data for drag/drop
  classCard.dataset.courseId = classItem.course_id || `${classItem.subject} ${classItem.number}`;
  classCard.dataset.courseTitle = classItem.title || classItem.description || "";
  classCard.dataset.courseUnits = classItem.units || 3;
  classCard.dataset.crn = classItem.crn || "";
  classCard.dataset.term = classItem.term;
  classCard.dataset.section = classItem.section || "";
  classCard.dataset.professor = classItem.professor || "";

  if (classItem.meetings && classItem.meetings.length > 0) {
    classCard.dataset.meetings = JSON.stringify(classItem.meetings);
  }

  // Hover animation
  classCard.addEventListener("mouseenter", () => {
    classCard.style.transform = "translateY(-2px)";
    classCard.style.boxShadow = "0 4px 8px rgba(0, 39, 76, 0.2)";
  });
  classCard.addEventListener("mouseleave", () => {
    classCard.style.transform = "translateY(0)";
    classCard.style.boxShadow = "none";
  });

  // ---- COURSE ID + SECTION ----
  const courseIdEl = document.createElement("strong");
  const sectionText = classItem.section ? ` - Section ${classItem.section}` : "";
  courseIdEl.textContent = `${classCard.dataset.courseId}${sectionText}`;
  courseIdEl.style.display = "block";
  courseIdEl.style.marginBottom = "5px";
  courseIdEl.style.color = "#00274C";

  // ---- TITLE ----
  const titleEl = document.createElement("span");
  titleEl.textContent = classItem.title || classItem.description || "No title available";
  titleEl.style.display = "block";
  titleEl.style.color = "#666";
  titleEl.style.fontSize = "14px";
  titleEl.style.marginBottom = "5px";

  // ---- PROFESSOR ----
  if (classItem.professor) {
    const professorEl = document.createElement("span");
    professorEl.textContent = `Professor: ${classItem.professor}`;
    professorEl.style.display = "block";
    professorEl.style.color = "#444";
    professorEl.style.fontSize = "13px";
    professorEl.style.marginBottom = "5px";
    classCard.appendChild(professorEl);

    // Fetch RMP rating async
    fetchProfessorRating(classItem.professor, professorEl);
  }

  // ---- UNITS ----
  const unitsEl = document.createElement("span");
  unitsEl.textContent = `${classItem.units || 3} units`;
  unitsEl.style.display = "block";
  unitsEl.style.color = "#444";
  unitsEl.style.fontSize = "13px";
  unitsEl.style.marginBottom = "5px";

  // ---- MEETING DAYS + TIME ----
  if (classItem.meetings && classItem.meetings.length > 0) {
    const meeting = classItem.meetings[0];

    // Days
    let days = "";
    if (meeting.days && Array.isArray(meeting.days)) {
      days = meeting.days.join(", ");
    } else if (meeting.day) {
      days = meeting.day;
    } else {
      days = "TBA";
    }

    // Time
    let time = "TBA";
    if (meeting.start !== undefined && meeting.end !== undefined) {
      const sH = Math.floor(meeting.start / 60);
      const sM = meeting.start % 60;
      const eH = Math.floor(meeting.end / 60);
      const eM = meeting.end % 60;

      const fmt = (h, m) => {
        const period = h >= 12 ? "PM" : "AM";
        const hr = h > 12 ? h - 12 : h === 0 ? 12 : h;
        return `${hr}:${m.toString().padStart(2, "0")} ${period}`;
      };

      time = `${fmt(sH, sM)} - ${fmt(eH, eM)}`;
    } else if (meeting.time) {
      time = meeting.time;
    }

    const meetingEl = document.createElement("span");
    meetingEl.textContent = `${days} | ${time}`;
    meetingEl.style.display = "block";
    meetingEl.style.color = "#00274C";
    meetingEl.style.fontWeight = "bold";
    meetingEl.style.fontSize = "13px";
    meetingEl.style.marginTop = "5px";
    classCard.appendChild(meetingEl);
  }

  // ---- CRN ----
  if (classItem.crn) {
    const crnEl = document.createElement("span");
    crnEl.textContent = `CRN: ${classItem.crn}`;
    crnEl.style.display = "block";
    crnEl.style.color = "#444";
    crnEl.style.fontSize = "12px";
    crnEl.style.marginTop = "5px";
    classCard.appendChild(crnEl);
  }

  // Append elements
  classCard.appendChild(courseIdEl);
  classCard.appendChild(titleEl);
  classCard.appendChild(unitsEl);

  // Drag handlers
  classCard.addEventListener("dragstart", handleDragStart);
  classCard.addEventListener("dragend", handleDragEnd);

  return classCard;
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
        
        // Handle new API format: { "Open Classes:": { "eligible_classes": [...] } }
        let classes = [];
        if (data && data["Open Classes:"] && data["Open Classes:"].eligible_classes) {
          classes = data["Open Classes:"].eligible_classes;
        } else if (Array.isArray(data)) {
          // Fallback to old format if needed
          classes = data;
        }
        
        return classes;
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
        classCard.dataset.section = classItem.section || '';
        classCard.dataset.professor = classItem.professor || '';
        
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
        
        // Course ID with section
        const courseIdEl = document.createElement('strong');
        const sectionText = classItem.section ? ` - Section ${classItem.section}` : '';
        courseIdEl.textContent = `${classCard.dataset.courseId}${sectionText}`;
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
        
        // Professor with rating
        if (classItem.professor) {
          const professorEl = document.createElement('span');
          professorEl.id = `professor-${classItem.crn}-${classItem.section}`;
          professorEl.textContent = `Professor: ${classItem.professor}`;
          professorEl.style.display = 'block';
          professorEl.style.color = '#666';
          professorEl.style.fontSize = '13px';
          professorEl.style.marginBottom = '5px';
          classCard.appendChild(professorEl);
          
          // Fetch and display professor rating asynchronously
          fetchProfessorRating(classItem.professor, professorEl);
        }
        
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
            let room = meeting.room || '';
            
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
            
            let meetingStr = `${day} ${time}`.trim();
            if (room) {
              meetingStr += ` (${room})`;
            }
            return meetingStr;
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
let draggedFromSchedule = false;

function handleDragStart(e) {
  draggedElement = e.target;
  draggedFromSchedule = false;
  e.target.style.opacity = '0.5';
  e.target.style.cursor = 'grabbing';
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', e.target.outerHTML);
}

function handleDragEnd(e) {
  e.target.style.opacity = '1';
  e.target.style.cursor = 'grab';
  draggedElement = null;
  draggedFromSchedule = false;
}

function handleScheduleDragStart(e) {
  draggedElement = e.target;
  draggedFromSchedule = true;
  e.target.style.opacity = '0.5';
  e.target.style.cursor = 'grabbing';
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', e.target.outerHTML);
}

function handleScheduleDragEnd(e) {
  e.target.style.opacity = '1';
  e.target.style.cursor = 'grab';
  // Don't reset draggedElement here - let the drop handler use it
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.dataTransfer.dropEffect = 'move';
  const dropZone = e.currentTarget;
  dropZone.style.border = '2px dashed #00274C';
  dropZone.style.backgroundColor = '#f0f7ff';
  return false;
}

function handleDragLeave(e) {
  const dropZone = e.currentTarget;
  // Only reset if we're actually leaving the panel (not just moving to a child)
  if (!dropZone.contains(e.relatedTarget)) {
    dropZone.style.border = 'none';
    dropZone.style.backgroundColor = '#ffffff';
  }
}

function handleDrop(e) {
  if (e.stopPropagation) e.stopPropagation();
  e.preventDefault();

  const schedulePanel = e.currentTarget;
  schedulePanel.style.border = "none";
  schedulePanel.style.backgroundColor = "#ffffff";

  if (!draggedElement || draggedFromSchedule) return;

  // Extract ALL stored data from the card
  const courseId = draggedElement.dataset.courseId;
  const courseTitle = draggedElement.dataset.courseTitle;
  const courseUnits = parseInt(draggedElement.dataset.courseUnits) || 3;
  const crn = draggedElement.dataset.crn || "";
  const professor = draggedElement.dataset.professor || "";
  const section = draggedElement.dataset.section || "";
  const meetingsRaw = draggedElement.dataset.meetings;

  // Prevent duplicates
  if (currentScheduleData.planned_courses.some(c => c.course_id === courseId)) {
    alert(`${courseId} is already in your schedule.`);
    return;
  }

  // Build full meeting object
  let meeting = { days: [], time: "TBA", room: "" };
  let fullMeetings = [];

  if (meetingsRaw) {
    try {
      fullMeetings = JSON.parse(meetingsRaw);

      if (fullMeetings.length > 0) {
        const m = fullMeetings[0];

        // Extract days
        if (m.days) meeting.days = m.days;
        else if (m.day) meeting.days = [m.day];

        // Extract room
        if (m.room) meeting.room = m.room;

        // Extract time
        if (m.start !== undefined && m.end !== undefined) {
          const format = mins => {
            const h = Math.floor(mins / 60);
            const m = mins % 60;
            const period = h >= 12 ? "PM" : "AM";
            const hh = h > 12 ? h - 12 : h === 0 ? 12 : h;
            return `${hh}:${m.toString().padStart(2, "0")} ${period}`;
          };
          meeting.time = `${format(m.start)} - ${format(m.end)}`;
        } else if (m.time) {
          meeting.time = m.time;
        }
      }
    } catch (err) {
      console.warn("Failed to parse meeting JSON:", err);
    }
  }

  // FINAL course object added into schedule
  const newCourse = {
    course_id: courseId,
    title: courseTitle,
    units: courseUnits,
    crn: crn,
    professor: professor,
    section: section,
    meeting: meeting,
    meetings: fullMeetings     // keep full detail for conflict checking
  };

  currentScheduleData.planned_courses.push(newCourse);
  currentScheduleData.planned_units += courseUnits;

  // Re-render schedule
  const scheduleList = document.getElementById("schedule-list");
  if (scheduleList) scheduleList.remove();

  renderSchedule();

  return false;
}


function handleScheduleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }
  
  e.preventDefault();
  const dropZone = e.currentTarget;
  dropZone.style.border = 'none';
  dropZone.style.backgroundColor = '#ffffff';
  
  if (!draggedElement || !draggedFromSchedule) return;
  
  // Get course index from dragged element
  const courseIndex = parseInt(draggedElement.dataset.courseIndex);
  if (isNaN(courseIndex)) return;
  
  // Remove course from schedule
  const removedCourse = currentScheduleData.planned_courses[courseIndex];
  if (removedCourse) {
    currentScheduleData.planned_courses.splice(courseIndex, 1);
    currentScheduleData.planned_units -= (removedCourse.units || 3);
    
    // Re-render schedule
    const scheduleList = document.getElementById('schedule-list');
    if (scheduleList) {
      scheduleList.remove();
    }
    renderSchedule();
    
    // Reset drag state
    draggedElement = null;
    draggedFromSchedule = false;
  }
  
  return false;
}

function initializeResultsPage() {
  // This will be populated when schedule is generated
  // For now, it's ready for backend integration
}

// ================= INITIALIZE ON PAGE LOAD =================
document.addEventListener('DOMContentLoaded', function() {
  initializeNavigation();
  initializeDayCheckboxes();
  initializeCalendarTimePicker();
  initializeUnitsSelector();
  initializeFileUpload();
  initializeGenerateButton();
  initializeResultsPage();
  
  console.log('Titan Scheduler initialized');
});
