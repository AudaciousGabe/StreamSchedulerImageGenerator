// Import required modules
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

// Create Express application
const app = express();
const PORT = process.env.PORT || 5555;

// LiveReload setup for development
if (process.env.NODE_ENV !== 'production') {
    const livereload = require('livereload');
    const connectLiveReload = require('connect-livereload');
    
    // Create a livereload server
    const liveReloadServer = livereload.createServer({
        exts: ['html', 'css', 'js', 'json'],
        debug: false
    });
    
    // Watch the current directory for changes
    liveReloadServer.watch(__dirname);
    
    // Inject livereload script into HTML pages
    app.use(connectLiveReload());
    
    // Log when files change
    liveReloadServer.server.once('connection', () => {
        setTimeout(() => {
            liveReloadServer.refresh('/');
        }, 100);
    });
}

// Middleware setup
app.use(cors()); // Allow cross-origin requests
app.use(express.json()); // Parse JSON request bodies
app.use(express.static(__dirname)); // Serve static files from current directory

// Configuration file path
const CONFIG_FILE = path.join(__dirname, 'config.json');

// Helper function to load config
function loadConfig() {
    try {
        if (fs.existsSync(CONFIG_FILE)) {
            const data = fs.readFileSync(CONFIG_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
    
    // Return default configuration if file doesn't exist or has errors
    return {
        channel: {
            name: "Audacious Gabe",
            link: "https://www.twitch.tv/audaciousgabe"
        },
        theme: "twilight",
        schedule: {
            today: {
                type: "normal"
            },
            tomorrow: {
                type: "work"
            }
        }
    };
}

// Helper function to save config
function saveConfig(config) {
    try {
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
        return true;
    } catch (error) {
        console.error('Error saving config:', error);
        return false;
    }
}

// API Routes

// GET /api/config - Get current configuration
app.get('/api/config', (req, res) => {
    console.log('📋 Config requested');
    const config = loadConfig();
    res.json(config);
});

// POST /api/config - Save new configuration
app.post('/api/config', (req, res) => {
    console.log('💾 Saving new config');
    const newConfig = req.body;
    
    if (saveConfig(newConfig)) {
        res.json({ success: true, message: 'Configuration saved successfully' });
    } else {
        res.status(500).json({ success: false, message: 'Failed to save configuration' });
    }
});

// GET /api/health - Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Main route - serve the HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'StreamSchedulerImageGenerator.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log('🚀 Stream Schedule Generator Server');
    console.log(`📡 Server running at: http://localhost:${PORT}`);
    console.log(`🎨 Open your browser to: http://localhost:${PORT}`);
    console.log('');
    console.log('Available endpoints:');
    console.log(`  GET  http://localhost:${PORT}/api/config - Get configuration`);
    console.log(`  POST http://localhost:${PORT}/api/config - Save configuration`);
    console.log(`  GET  http://localhost:${PORT}/api/health - Health check`);
    console.log('');
    console.log('Press Ctrl+C to stop the server');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down server...');
    process.exit(0);
});
