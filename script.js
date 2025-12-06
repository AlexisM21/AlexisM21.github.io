// script.js

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
function initializeGenerateButton() {
  const generateButton = document.querySelector('#upload-panel button');
  
  if (generateButton) {
    generateButton.addEventListener('click', function() {
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
      
      // Build times summary
      let timesSummary = '';
      const daysWithTimes = Object.keys(preferences.preferredTimesByDay).filter(day => 
        preferences.preferredTimesByDay[day].length > 0
      );
      
      if (daysWithTimes.length > 0) {
        timesSummary = daysWithTimes.map(day => {
          const times = preferences.preferredTimesByDay[day].join(', ');
          return `${day}: ${times}`;
        }).join('\n');
      } else {
        timesSummary = 'Any time';
      }
      
      // For now, just show a message (backend will be connected later)
      console.log('Generating schedule with preferences:', preferences);
      alert('Schedule generation will be implemented once backend is connected.\n\nCurrent preferences:\n- Days: ' + preferences.preferredDays.join(', ') + '\n- Times:\n' + timesSummary + '\n- Units: ' + preferences.preferredUnits + '\n- File: ' + preferences.uploadedFile.name);
      
      // In the future, this will make an API call to generate the schedule
      // For now, we'll just navigate to results page
      showPage('step-results');
    });
  }
}

// ================= RESULTS PAGE =================
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

