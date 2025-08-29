// Dynamic Editor Slot Management System
// This manages slots in the EDITOR only, keeping the display area clean

class EditorSlotManager {
    constructor() {
        this.slots = {
            todayNormal: [],
            todayWork: [],
            tomorrowNormal: [],
            tomorrowWork: []
        };
        
        // Default slot data
        this.defaultSlots = {
            normal: [
                { time: "9:30 AM - 12:30 PM", title: "Morning Warmup", desc: "Clearing admin tasks, then jumping into chill development." },
                { time: "1:00 PM - 4:00 PM", title: "Focused Development + Prototype Speedrun", desc: "Getting stuff done and making things happen ✨👏" },
                { time: "5:00 PM - 8:00 PM", title: "Greenlight Development", desc: "You picked it, now we're building it." },
                { time: "9:00 PM - 12:00 AM", title: "Late Night Admin", desc: "Winding down with some chill development." }
            ],
            work: [
                { time: "9:30 AM - 12:30 PM", title: "Morning Warmup", desc: "Clearing admin tasks, then jumping into chill development." },
                { time: "12:30 PM - 3:30 PM", title: "Focused Development + Prototype Speedrun", desc: "Getting stuff done and making things happen ✨👏" }
            ]
        };
        
        this.init();
    }
    
    init() {
        // Initialize with default slots
        this.slots.todayNormal = [...this.defaultSlots.normal];
        this.slots.todayWork = [...this.defaultSlots.work];
        this.slots.tomorrowNormal = [...this.defaultSlots.normal];
        this.slots.tomorrowWork = [...this.defaultSlots.work];
        
        // Load saved slots from localStorage if available
        this.loadSavedSlots();
        
        // Setup editor containers
        this.setupEditorContainers();
        
        // Render all editor slots
        this.renderAllEditorSlots();
        
        // Update display areas
        this.updateAllDisplays();
    }
    
    loadSavedSlots() {
        const saved = localStorage.getItem('editorStreamSlots');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                this.slots = parsed;
            } catch (e) {
                console.error('Failed to load saved slots:', e);
            }
        }
    }
    
    saveSlots() {
        localStorage.setItem('editorStreamSlots', JSON.stringify(this.slots));
        this.updateAllDisplays();
    }
    
    setupEditorContainers() {
        // Create dynamic containers in the editor sections if they don't exist
        const todayEditor = document.getElementById('todayEditor');
        const tomorrowEditor = document.getElementById('tomorrowEditor');
        
        // Find or create containers for dynamic slots
        ['todayNormal', 'todayWork'].forEach(slotKey => {
            if (!document.getElementById(`${slotKey}EditorContainer`)) {
                // This will be injected into existing HTML structure
            }
        });
        
        ['tomorrowNormal', 'tomorrowWork'].forEach(slotKey => {
            if (!document.getElementById(`${slotKey}EditorContainer`)) {
                // This will be injected into existing HTML structure  
            }
        });
    }
    
    renderAllEditorSlots() {
        this.renderEditorSlots('todayNormal');
        this.renderEditorSlots('todayWork');
        this.renderEditorSlots('tomorrowNormal');
        this.renderEditorSlots('tomorrowWork');
    }
    
    renderEditorSlots(slotKey) {
        const containerId = `${slotKey}EditorContainer`;
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create slot inputs
        this.slots[slotKey].forEach((slot, index) => {
            const slotDiv = document.createElement('div');
            slotDiv.className = 'slot-editor-row flex items-center gap-2 mb-3';
            slotDiv.innerHTML = `
                <div class="flex-grow grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <input type="text" 
                           id="${slotKey}Slot${index + 1}TitleInput" 
                           placeholder="Slot ${index + 1} Title" 
                           class="editor-input rounded p-2" 
                           value="${slot.title}">
                    <input type="text" 
                           id="${slotKey}Slot${index + 1}DescInput" 
                           placeholder="Slot ${index + 1} Description" 
                           class="editor-input rounded p-2" 
                           value="${slot.desc}">
                </div>
                <input type="text" 
                       id="${slotKey}Slot${index + 1}TimeInput" 
                       placeholder="Time" 
                       class="editor-input rounded p-2 w-40" 
                       value="${slot.time}">
                <button onclick="editorSlotManager.deleteSlot('${slotKey}', ${index})" 
                        class="delete-editor-btn bg-red-500 hover:bg-red-600 text-white p-2 rounded transition-colors"
                        title="Delete this slot">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;
            container.appendChild(slotDiv);
            
            // Add event listeners for inputs
            const titleInput = slotDiv.querySelector(`#${slotKey}Slot${index + 1}TitleInput`);
            const descInput = slotDiv.querySelector(`#${slotKey}Slot${index + 1}DescInput`);
            const timeInput = slotDiv.querySelector(`#${slotKey}Slot${index + 1}TimeInput`);
            
            titleInput.addEventListener('input', (e) => {
                this.slots[slotKey][index].title = e.target.value;
                this.updateDisplay(slotKey, index);
                this.saveSlots();
            });
            
            descInput.addEventListener('input', (e) => {
                this.slots[slotKey][index].desc = e.target.value;
                this.updateDisplay(slotKey, index);
                this.saveSlots();
            });
            
            timeInput.addEventListener('input', (e) => {
                this.slots[slotKey][index].time = e.target.value;
                this.updateDisplay(slotKey, index);
                this.saveSlots();
            });
        });
        
        // Add the "Add Slot" button
        const addButton = document.createElement('button');
        addButton.className = 'add-editor-btn bg-[var(--btn-active-bg)] hover:opacity-90 text-white font-semibold py-2 px-4 rounded-lg transition-opacity w-full mt-2';
        addButton.textContent = '+ Add Stream Slot';
        addButton.onclick = () => this.addSlot(slotKey);
        container.appendChild(addButton);
    }
    
    addSlot(slotKey) {
        // Determine default time based on last slot
        const slots = this.slots[slotKey];
        let defaultTime = "2:00 PM - 5:00 PM";
        
        if (slots.length > 0) {
            // Try to parse the last slot's end time and add 30 minutes
            const lastTime = slots[slots.length - 1].time;
            const endTimeMatch = lastTime.match(/- (\d{1,2}):(\d{2}) (AM|PM)/);
            if (endTimeMatch) {
                let hours = parseInt(endTimeMatch[1]);
                let minutes = parseInt(endTimeMatch[2]);
                const ampm = endTimeMatch[3];
                
                // Convert to 24-hour format
                if (ampm === 'PM' && hours !== 12) hours += 12;
                if (ampm === 'AM' && hours === 12) hours = 0;
                
                // Add 30 minutes for start time
                minutes += 30;
                if (minutes >= 60) {
                    hours += 1;
                    minutes -= 60;
                }
                
                // Calculate end time (3 hours later)
                let endHours = hours + 3;
                let endMinutes = minutes;
                
                // Convert back to 12-hour format
                const startAmPm = hours >= 12 ? 'PM' : 'AM';
                const endAmPm = endHours >= 12 ? 'PM' : 'AM';
                
                const startHour12 = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
                const endHour12 = endHours > 12 ? endHours - 12 : (endHours === 0 ? 12 : endHours);
                
                defaultTime = `${startHour12}:${minutes.toString().padStart(2, '0')} ${startAmPm} - ${endHour12}:${endMinutes.toString().padStart(2, '0')} ${endAmPm}`;
            }
        }
        
        const newSlot = {
            time: defaultTime,
            title: "New Stream Session",
            desc: "Description of this stream session"
        };
        
        this.slots[slotKey].push(newSlot);
        this.saveSlots();
        this.renderEditorSlots(slotKey);
        this.updateDisplayForSlotKey(slotKey);
    }
    
    deleteSlot(slotKey, index) {
        if (this.slots[slotKey].length <= 1) {
            alert("You must have at least one stream slot!");
            return;
        }
        
        if (confirm("Are you sure you want to delete this stream slot?")) {
            this.slots[slotKey].splice(index, 1);
            this.saveSlots();
            this.renderEditorSlots(slotKey);
            this.updateDisplayForSlotKey(slotKey);
        }
    }
    
    updateDisplay(slotKey, slotIndex) {
        // Map editor slot keys to display element IDs
        const slot = this.slots[slotKey][slotIndex];
        if (!slot) return;
        
        let displayTitleId, displayDescId, displayTimeContainerId;
        
        // Determine the display element IDs based on slotKey
        const isToday = slotKey.startsWith('today');
        const isNormal = slotKey.includes('Normal');
        
        if (slotKey === 'todayNormal') {
            displayTitleId = `todayNormalSlot${slotIndex + 1}Title`;
            displayDescId = `todayNormalSlot${slotIndex + 1}Desc`;
            displayTimeContainerId = `todayNormalSlot${slotIndex + 1}Time`;
        } else if (slotKey === 'todayWork') {
            displayTitleId = `todayWorkSlot${slotIndex + 1}Title`;
            displayDescId = `todayWorkSlot${slotIndex + 1}Desc`;
            displayTimeContainerId = `todayWorkSlot${slotIndex + 1}Time`;
        } else if (slotKey === 'tomorrowNormal') {
            displayTitleId = `tomorrowNormalSlot${slotIndex + 1}Title`;
            displayDescId = `tomorrowNormalSlot${slotIndex + 1}Desc`;
            displayTimeContainerId = `tomorrowNormalSlot${slotIndex + 1}Time`;
        } else if (slotKey === 'tomorrowWork') {
            displayTitleId = `tomorrowWorkSlot${slotIndex + 1}Title`;
            displayDescId = `tomorrowWorkSlot${slotIndex + 1}Desc`;
            displayTimeContainerId = `tomorrowWorkSlot${slotIndex + 1}Time`;
        }
        
        // Update the display elements
        const titleEl = document.getElementById(displayTitleId);
        const descEl = document.getElementById(displayDescId);
        
        if (titleEl) titleEl.textContent = slot.title;
        if (descEl) descEl.textContent = slot.desc;
        
        // Update time if we have a container for it
        const timeContainer = document.getElementById(displayTimeContainerId);
        if (timeContainer) {
            const timeP = timeContainer.querySelector('p');
            if (timeP) timeP.textContent = slot.time;
        }
    }
    
    updateDisplayForSlotKey(slotKey) {
        // Get the display container
        let displayContainerId;
        if (slotKey === 'todayNormal') displayContainerId = 'normalDayScheduleToday';
        else if (slotKey === 'todayWork') displayContainerId = 'workDayScheduleToday';
        else if (slotKey === 'tomorrowNormal') displayContainerId = 'normalDayScheduleTomorrow';
        else if (slotKey === 'tomorrowWork') displayContainerId = 'workDayScheduleTomorrow';
        
        const container = document.getElementById(displayContainerId);
        if (!container) return;
        
        // Clear and rebuild the display
        container.innerHTML = '';
        
        const isToday = slotKey.startsWith('today');
        
        // Determine colors based on today/tomorrow
        const bgClass = isToday ? 'bg-[var(--tomorrow-bg)]' : 'bg-[var(--bg-secondary)]';
        const borderClass = isToday ? 'border-[var(--tomorrow-border)]' : 'border-[var(--border-primary)]';
        const accentBgClass = isToday ? 'bg-[var(--tomorrow-accent-bg)]' : 'bg-[var(--today-accent-bg)]';
        const textClass = isToday ? 'text-[var(--tomorrow-text)]' : 'text-[var(--today-accent)]';
        const titleTextClass = isToday ? 'text-[var(--tomorrow-text)]' : 'text-[var(--text-primary)]';
        
        // Render each slot WITHOUT any controls
        this.slots[slotKey].forEach((slot, index) => {
            const slotDiv = document.createElement('div');
            slotDiv.className = `${bgClass} backdrop-blur-sm rounded-xl p-5 border ${borderClass} flex items-center gap-4`;
            
            const slotIdPrefix = `${slotKey}Slot${index + 1}`;
            
            slotDiv.innerHTML = `
                <div id="${slotIdPrefix}Time" class="${accentBgClass} ${textClass} font-bold rounded-lg px-4 py-3 text-center w-48 flex items-center justify-center">
                    <p>${slot.time}</p>
                </div>
                <div>
                    <h3 id="${slotIdPrefix}Title" class="text-xl font-semibold ${titleTextClass}">${slot.title}</h3>
                    <p id="${slotIdPrefix}Desc" class="text-[var(--text-secondary)] mt-1">${slot.desc}</p>
                </div>
            `;
            
            container.appendChild(slotDiv);
        });
    }
    
    updateAllDisplays() {
        Object.keys(this.slots).forEach(slotKey => {
            this.updateDisplayForSlotKey(slotKey);
        });
    }
}

// Initialize the editor slot manager when the document is ready
let editorSlotManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        editorSlotManager = new EditorSlotManager();
    });
} else {
    editorSlotManager = new EditorSlotManager();
}
