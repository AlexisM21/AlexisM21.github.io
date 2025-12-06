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
  preferredTimes: [],
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

// ================= TIME PICKER =================
function initializeTimePicker() {
  const timeItems = document.querySelectorAll('.time-item');
  const timePicker = document.querySelector('.time-picker');
  
  // Make time items selectable
  timeItems.forEach(item => {
    item.style.cursor = 'pointer';
    item.style.userSelect = 'none';
    item.style.transition = 'background-color 0.2s';
    
    // Add click handler
    item.addEventListener('click', function() {
      const time = this.textContent.trim();
      
      // Toggle selection
      if (this.classList.contains('selected')) {
        this.classList.remove('selected');
        preferences.preferredTimes = preferences.preferredTimes.filter(t => t !== time);
        this.style.backgroundColor = '';
        this.style.color = '';
      } else {
        this.classList.add('selected');
        if (!preferences.preferredTimes.includes(time)) {
          preferences.preferredTimes.push(time);
        }
        this.style.backgroundColor = '#00274C';
        this.style.color = 'white';
      }
      
      console.log('Preferred times:', preferences.preferredTimes);
    });
    
    // Add hover effect
    item.addEventListener('mouseenter', function() {
      if (!this.classList.contains('selected')) {
        this.style.backgroundColor = '#e0e0e0';
      }
    });
    
    item.addEventListener('mouseleave', function() {
      if (!this.classList.contains('selected')) {
        this.style.backgroundColor = '';
      }
    });
  });
  
  // Add scroll snapping behavior for better UX
  const timeList = document.querySelector('.time-list');
  if (timeList) {
    timeList.addEventListener('scroll', function() {
      // Optional: Auto-select time on scroll (if desired)
      // For now, we'll keep manual selection
    });
  }
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
      
      // For now, just show a message (backend will be connected later)
      console.log('Generating schedule with preferences:', preferences);
      alert('Schedule generation will be implemented once backend is connected.\n\nCurrent preferences:\n- Days: ' + preferences.preferredDays.join(', ') + '\n- Times: ' + (preferences.preferredTimes.length > 0 ? preferences.preferredTimes.join(', ') : 'Any time') + '\n- Units: ' + preferences.preferredUnits + '\n- File: ' + preferences.uploadedFile.name);
      
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
  initializeTimePicker();
  initializeUnitsSelector();
  initializeFileUpload();
  initializeGenerateButton();
  initializeResultsPage();
  
  console.log('Titan Scheduler initialized');
});
