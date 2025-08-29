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
                <div class="relative">
                    <input type="text" 
                           id="${slotKey}Slot${index + 1}TimeInput" 
                           placeholder="Time" 
                           class="editor-input rounded p-2 w-44 cursor-pointer font-semibold" 
                           value="${slot.time}"
                           readonly>
                </div>
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
            
            // Add click handler for time picker
            timeInput.addEventListener('click', (e) => {
                this.showTimePicker(e.target, slotKey, index);
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
    
    showTimePicker(inputElement, slotKey, slotIndex) {
        // Remove any existing picker overlay
        const existing = document.getElementById('mdTimeRangePicker');
        if (existing) existing.remove();

        // Theme colors
        const cs = getComputedStyle(document.body);
        const bg = cs.getPropertyValue('--bg-primary').trim() || '#111827';
        const border = cs.getPropertyValue('--border-primary').trim() || 'rgba(55, 65, 81, 0.5)';
        const text = cs.getPropertyValue('--text-primary').trim() || '#f9fafb';
        const textSecondary = cs.getPropertyValue('--text-secondary').trim() || '#d1d5db';
        const muted = cs.getPropertyValue('--text-muted').trim() || '#6b7280';
        const accent = cs.getPropertyValue('--btn-active-bg').trim() || '#9333ea';
        const inputBg = cs.getPropertyValue('--input-bg').trim() || '#374151';

        // Parse current time range
        const currentTime = this.slots[slotKey][slotIndex].time;
        const match = currentTime.match(/(\d{1,2}):(\d{2}) (AM|PM) - (\d{1,2}):(\d{2}) (AM|PM)/);
        let start = { h: 9, m: 30, a: 'AM' };
        let end = { h: 12, m: 30, a: 'PM' };
        if (match) {
            start.h = parseInt(match[1]); start.m = parseInt(match[2]); start.a = match[3];
            end.h = parseInt(match[4]); end.m = parseInt(match[5]); end.a = match[6];
        }

        // State
        let step = 'start'; // 'start' | 'end'
        let mode = 'hour'; // 'hour' | 'minute'

        const formatTime = (t) => `${t.h}:${t.m.toString().padStart(2,'0')} ${t.a}`;

        // Build overlay (no translucent backdrop to keep opaque spec)
        const overlay = document.createElement('div');
        overlay.id = 'mdTimeRangePicker';
        overlay.setAttribute('role', 'dialog');
        overlay.style.position = 'fixed';
        overlay.style.inset = '0';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.zIndex = '1000';
        overlay.style.background = 'transparent';

        const card = document.createElement('div');
        card.style.width = '360px';
        card.style.maxWidth = '92vw';
        card.style.background = bg;
        card.style.border = `1px solid ${border}`;
        card.style.borderRadius = '16px';
        card.style.boxShadow = '0 20px 40px rgba(0,0,0,0.5)';
        card.style.padding = '16px';
        card.style.color = text;
        card.style.fontFamily = 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif';

        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.justifyContent = 'space-between';
        header.style.marginBottom = '8px';

        const title = document.createElement('div');
        title.style.fontSize = '14px';
        title.style.fontWeight = '600';
        title.style.color = textSecondary;
        title.textContent = 'Select start time';

        const ampmWrap = document.createElement('div');
        ampmWrap.style.display = 'flex';
        ampmWrap.style.gap = '8px';

        const amBtn = document.createElement('button');
        const pmBtn = document.createElement('button');
        const styleAmPmBtn = (btn, active) => {
            btn.style.padding = '6px 10px';
            btn.style.borderRadius = '9999px';
            btn.style.border = `1px solid ${border}`;
            btn.style.background = active ? accent : inputBg;
            btn.style.color = active ? '#ffffff' : text;
            btn.style.fontWeight = '600';
        };
        amBtn.textContent = 'AM';
        pmBtn.textContent = 'PM';

        amBtn.addEventListener('click', () => {
            if (step === 'start') start.a = 'AM'; else end.a = 'AM';
            syncAmPm();
        });
        pmBtn.addEventListener('click', () => {
            if (step === 'start') start.a = 'PM'; else end.a = 'PM';
            syncAmPm();
        });
        const syncAmPm = () => {
            const active = step === 'start' ? start.a : end.a;
            styleAmPmBtn(amBtn, active === 'AM');
            styleAmPmBtn(pmBtn, active === 'PM');
            currentReadout.textContent = step === 'start' ? formatTime(start) : formatTime(end);
        };

        ampmWrap.appendChild(amBtn);
        ampmWrap.appendChild(pmBtn);

        header.appendChild(title);
        header.appendChild(ampmWrap);

        // Readout
        const currentReadout = document.createElement('div');
        currentReadout.style.fontSize = '28px';
        currentReadout.style.fontWeight = '800';
        currentReadout.style.letterSpacing = '0.5px';
        currentReadout.style.margin = '6px 0 10px 0';
        currentReadout.style.color = text;
        currentReadout.textContent = formatTime(start);

        // Clock container
        const clockBox = document.createElement('div');
        clockBox.style.position = 'relative';
        clockBox.style.width = '300px';
        clockBox.style.height = '300px';
        clockBox.style.margin = '0 auto';
        clockBox.style.borderRadius = '9999px';
        clockBox.style.background = inputBg;
        clockBox.style.border = `1px solid ${border}`;
        clockBox.style.boxShadow = 'inset 0 0 20px rgba(0,0,0,0.25)';

        const centerDot = document.createElement('div');
        centerDot.style.position = 'absolute';
        centerDot.style.width = '10px';
        centerDot.style.height = '10px';
        centerDot.style.borderRadius = '9999px';
        centerDot.style.left = '50%';
        centerDot.style.top = '50%';
        centerDot.style.transform = 'translate(-50%, -50%)';
        centerDot.style.background = accent;
        clockBox.appendChild(centerDot);

        // Footer actions
        const footer = document.createElement('div');
        footer.style.display = 'flex';
        footer.style.gap = '8px';
        footer.style.marginTop = '14px';

        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.flex = '1';
        cancelBtn.style.padding = '10px 12px';
        cancelBtn.style.borderRadius = '10px';
        cancelBtn.style.border = `1px solid ${border}`;
        cancelBtn.style.background = inputBg;
        cancelBtn.style.color = text;
        cancelBtn.style.fontWeight = '700';

        const backBtn = document.createElement('button');
        backBtn.textContent = 'Back';
        backBtn.style.flex = '1';
        backBtn.style.padding = '10px 12px';
        backBtn.style.borderRadius = '10px';
        backBtn.style.border = `1px solid ${border}`;
        backBtn.style.background = inputBg;
        backBtn.style.color = text;
        backBtn.style.fontWeight = '700';
        backBtn.disabled = true;
        backBtn.style.opacity = '0.6';

        const nextBtn = document.createElement('button');
        nextBtn.textContent = 'Next';
        nextBtn.style.flex = '1';
        nextBtn.style.padding = '10px 12px';
        nextBtn.style.borderRadius = '10px';
        nextBtn.style.border = `1px solid ${border}`;
        nextBtn.style.background = accent;
        nextBtn.style.color = '#ffffff';
        nextBtn.style.fontWeight = '800';

        const applyBtn = document.createElement('button');
        applyBtn.textContent = 'Apply';
        applyBtn.style.flex = '1';
        applyBtn.style.padding = '10px 12px';
        applyBtn.style.borderRadius = '10px';
        applyBtn.style.border = `1px solid ${border}`;
        applyBtn.style.background = accent;
        applyBtn.style.color = '#ffffff';
        applyBtn.style.fontWeight = '800';
        applyBtn.style.display = 'none';

        footer.appendChild(cancelBtn);
        footer.appendChild(backBtn);
        footer.appendChild(nextBtn);
        footer.appendChild(applyBtn);

        // Assemble card
        card.appendChild(header);
        card.appendChild(currentReadout);
        card.appendChild(clockBox);
        card.appendChild(footer);
        overlay.appendChild(card);

        // Insert into DOM
        document.body.appendChild(overlay);

        // Helpers to render clock marks
        const clearMarks = () => {
            // Remove all existing mark nodes except centerDot
            [...clockBox.querySelectorAll('.mdtp-mark')].forEach(n => n.remove());
        };
        const createMark = (label, angleDeg, selected) => {
            const r = 120; // radius to place marks
            const cx = 150, cy = 150; // center of 300x300
            const rad = (angleDeg - 90) * Math.PI / 180; // rotate so 12 is at top
            const x = cx + r * Math.cos(rad);
            const y = cy + r * Math.sin(rad);
            const el = document.createElement('div');
            el.className = 'mdtp-mark';
            el.textContent = label;
            el.style.position = 'absolute';
            el.style.left = `${x}px`;
            el.style.top = `${y}px`;
            el.style.transform = 'translate(-50%, -50%)';
            el.style.width = '44px';
            el.style.height = '44px';
            el.style.lineHeight = '44px';
            el.style.textAlign = 'center';
            el.style.borderRadius = '9999px';
            el.style.cursor = 'pointer';
            el.style.userSelect = 'none';
            el.style.fontWeight = '700';
            el.style.fontSize = '14px';
            el.style.background = selected ? accent : bg;
            el.style.border = `1px solid ${border}`;
            el.style.color = selected ? '#ffffff' : text;
            el.style.boxShadow = selected ? '0 0 0 4px rgba(147,51,234,0.35)' : 'none';
            return el;
        };

        const renderHourMarks = () => {
            clearMarks();
            const active = step === 'start' ? start : end;
            for (let i = 1; i <= 12; i++) {
                const angle = i * 30; // 360/12
                const mark = createMark(String(i), angle, active.h === i);
                mark.addEventListener('click', () => {
                    active.h = i;
                    currentReadout.textContent = step === 'start' ? formatTime(start) : formatTime(end);
                    renderMinuteMarks();
                    backBtn.disabled = false; backBtn.style.opacity = '1';
                });
                clockBox.appendChild(mark);
            }
        };

        const renderMinuteMarks = () => {
            clearMarks();
            const active = step === 'start' ? start : end;
            const values = [0,5,10,15,20,25,30,35,40,45,50,55];
            values.forEach((v, idx) => {
                const angle = idx * 30; // 12 positions
                const label = v.toString().padStart(2,'0');
                const mark = createMark(label, angle, active.m === v);
                mark.addEventListener('click', () => {
                    active.m = v;
                    currentReadout.textContent = step === 'start' ? formatTime(start) : formatTime(end);
                    // If we're on start minutes, move to end hours; else show apply
                    if (step === 'start') {
                        step = 'end';
                        mode = 'hour';
                        title.textContent = 'Select end time';
                        syncAmPm();
                        renderHourMarks();
                        backBtn.disabled = false; backBtn.style.opacity = '1';
                    } else {
                        // end minutes selected, show apply
                        nextBtn.style.display = 'none';
                        applyBtn.style.display = 'block';
                    }
                });
                clockBox.appendChild(mark);
            });
        };

        // Wire buttons
        cancelBtn.addEventListener('click', () => overlay.remove());
        backBtn.addEventListener('click', () => {
            // Navigate backwards across modes/steps
            if (step === 'end' && mode === 'minute') {
                mode = 'hour';
                renderHourMarks();
                nextBtn.style.display = 'block';
                applyBtn.style.display = 'none';
            } else if (step === 'end' && mode === 'hour') {
                step = 'start';
                mode = 'minute';
                title.textContent = 'Select start time';
                syncAmPm();
                renderMinuteMarks();
            } else if (step === 'start' && mode === 'minute') {
                mode = 'hour';
                renderHourMarks();
                backBtn.disabled = true; backBtn.style.opacity = '0.6';
            }
        });
        nextBtn.addEventListener('click', () => {
            if (mode === 'hour') {
                mode = 'minute';
                renderMinuteMarks();
            } else if (mode === 'minute') {
                // Only visible when on end step handled above; keep for safety
                step = 'end';
                mode = 'hour';
                title.textContent = 'Select end time';
                syncAmPm();
                renderHourMarks();
            }
        });
        applyBtn.addEventListener('click', () => {
            const newTime = `${formatTime(start)} - ${formatTime(end)}`;
            inputElement.value = newTime;
            this.slots[slotKey][slotIndex].time = newTime;
            this.updateDisplay(slotKey, slotIndex);
            this.saveSlots();
            overlay.remove();
        });

        // Close on outside click or ESC
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });
        const escHandler = (e) => { if (e.key === 'Escape') { overlay.remove(); document.removeEventListener('keydown', escHandler); } };
        document.addEventListener('keydown', escHandler);

        // Initial render: start hour selection
        syncAmPm();
        renderHourMarks();
        nextBtn.style.display = 'block';
        applyBtn.style.display = 'none';
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
