/**
 * WordTree Component using wordcloud2.js
 * 
 * A word cloud visualization that displays words as leaves on a tree with a trunk.
 * FORCE FILL mode - Eliminates all whitespace around the cloud.
 */

class WordTree {
    constructor(containerId, options = {}) {
        console.log('WordTree constructor called for:', containerId);
        
        this.containerId = containerId;
        
        // Find the container with the correct ID
        this.container = document.getElementById(`wordtree-${containerId}`);
        
        if (!this.container) {
            console.error(`Container #wordtree-${containerId} not found!`);
            console.log('Available containers:', Array.from(document.querySelectorAll('[id^="wordtree-"]')).map(el => el.id));
            return;
        }
        
        console.log('Container found successfully');
        
        this.canvas = document.getElementById(`wordcloud-canvas-${containerId}`);
        this.loadingEl = document.getElementById(`loading-${containerId}`);
        this.errorEl = document.getElementById(`error-${containerId}`);
        this.wordCountEl = document.getElementById(`word-count-${containerId}`);
        
        if (!this.canvas) {
            console.error(`Canvas #wordcloud-canvas-${containerId} not found!`);
            return;
        }

        console.log('Canvas found successfully');

        // Force canvas to fill its container with no gaps
        this.forceCanvasSize();
        
        // Get data from data attribute
        const dataElement = document.getElementById(`wordtree-data-${containerId}`);
        if (dataElement && dataElement.dataset.json) {
            try {
                const jsonString = dataElement.dataset.json;
                this.wordData = JSON.parse(jsonString);
                console.log('Word data loaded:', this.wordData.words.length, 'words');
            } catch (e) {
                console.error('Failed to parse word tree data:', e);
                this.wordData = { words: [], total_count: 0 };
            }
        } else {
            console.warn('No word tree data found for container:', containerId);
            this.wordData = { words: [], total_count: 0 };
        }
        
        // CRITICAL: These options are tuned to ELIMINATE WHITESPACE
        this.options = {
            // Smaller grid size = more precise placement
            gridSize: 8,
            
            // Weight factor to make words fill the space
            weightFactor: function(weight) {
                // Scale words to fill the canvas based on available dimensions
                return Math.pow(weight, 0.55) * 18;
            },
            
            fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
            color: this.getWordColor.bind(this),
            
            // Rotate some words to fill space better
            rotateRatio: 0.3,
            rotationSteps: 2,
            
            backgroundColor: 'transparent',
            
            // Shape function to maximize fill
            shape: this.getFillShape.bind(this),
            
            // Minimum font size
            minSize: 10,
            
            // Don't shrink to fit - we want to fill the space
            shrinkToFit: false,
            
            // Origin at top to eliminate top margin
            origin: [0.5, 0.25], // Moved way up to eliminate top whitespace
            
            // Make words slightly elliptical to fill width better
            ellipticity: 1.0,
            
            // Disable drawing out of bounds to prevent clipping
            drawOutOfBound: false,
            
            // Clear canvas before drawing
            clearCanvas: true,
            
            // Click handler
            click: (item, dimension, event) => {
                if (item && item[0]) {
                    this.handleWordClick(item[0]);
                }
            },
            
            // No hover effect for performance
            hover: null,
            
            // Use size weighting
            weightMode: 'size',
            
            // Don't shuffle - keep consistent layout
            shuffle: false,
            
            ...options
        };
        
        this.currentFilters = this.getFiltersFromURL();
        this.cloudInstance = null;
        this.resizeTimeout = null;
        
        // Initialize with a slight delay to ensure DOM is ready
        setTimeout(() => this.init(), 50);
    }
    
    /**
     * Force canvas to have exactly the right size with no margins
     */
    forceCanvasSize() {
        if (!this.canvas) return;
        
        // Get the parent container that has flex: 1 1 auto
        const container = this.canvas.parentElement;
        if (!container) return;
        
        // Get the grootste container
        const wordtreeContainer = container.parentElement;
        if (!wordtreeContainer) return;
        
        // Force dimensions based on the flex container
        const containerRect = wordtreeContainer.getBoundingClientRect();
        
        // Calculate available height (total height minus trunk height)
        const trunkHeight = 70; // Match the trunk container height
        const availableHeight = Math.max(500, containerRect.height - trunkHeight - 10);
        
        // Set canvas dimensions with NO PADDING
        this.canvas.width = containerRect.width;
        this.canvas.height = availableHeight;
        
        // Also set CSS dimensions to match
        this.canvas.style.width = containerRect.width + 'px';
        this.canvas.style.height = availableHeight + 'px';
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        
        console.log(`Canvas FORCED to ${containerRect.width}x${availableHeight} (no margins)`);
        
        return {
            width: containerRect.width,
            height: availableHeight
        };
    }
    
    /**
     * Shape function that makes words fill the entire top portion
     */
    getFillShape(theta) {
        // Normalize theta to 0-2PI
        const normalizedTheta = theta < 0 ? theta + 2 * Math.PI : theta;
        
        // We want the shape to be a full circle/ellipse that touches the top
        // and sides, but leaves a small gap at the bottom for the trunk
        
        // Base ellipticity - make it slightly elliptical to fill width
        const baseRadius = 0.95;
        
        // If this is the bottom portion (where trunk goes), flatten slightly
        if (normalizedTheta > 1.8 && normalizedTheta < 4.5) {
            // Bottom - flatten to create connection point for trunk
            return baseRadius * 0.85;
        }
        
        // Top and sides - full radius to fill space
        return baseRadius;
    }
    
    getFiltersFromURL() {
        const params = new URLSearchParams(window.location.search);
        return {
            date: params.get('date_filter') || 'all',
            activity: params.get('activity_filter') || 'all'
        };
    }
    
    init() {
        console.log('Initializing WordTree with', this.wordData.words ? this.wordData.words.length : 0, 'words');
        
        if (this.wordData.words && this.wordData.words.length > 0) {
            // Force canvas size one more time before rendering
            this.forceCanvasSize();
            this.render();
        } else {
            this.showEmptyState();
        }
        
        this.setupFilterControls();
        this.setupEventListeners();
    }
    
    render() {
        if (!this.canvas) return;
        
        if (!this.wordData.words || this.wordData.words.length === 0) {
            this.showEmptyState();
            return;
        }

        // Check if WordCloud is available
        if (!window.WordCloud) {
            console.error('WordCloud2 is not loaded');
            this.showError('WordCloud library not loaded');
            return;
        }

        if (!window.WordCloud.isSupported) {
            console.error('WordCloud2 is not supported in this browser');
            this.showError('WordCloud is not supported in this browser');
            return;
        }
        
        // Update word count
        if (this.wordCountEl) {
            this.wordCountEl.textContent = this.wordData.total_count || this.wordData.words.length;
        }
        
        // Prepare data for wordcloud2: [['word', weight], ...]
        // Scale weights to ensure good distribution
        const maxWeight = Math.max(...this.wordData.words.map(w => w.weight));
        const minWeight = Math.min(...this.wordData.words.map(w => w.weight));
        const weightRange = maxWeight - minWeight;
        
        const words = this.wordData.words.map(item => {
            // Normalize weight to ensure good size variation
            let normalizedWeight = item.weight;
            if (weightRange > 0) {
                normalizedWeight = 0.5 + ((item.weight - minWeight) / weightRange) * 1.5;
            }
            return [item.word, normalizedWeight];
        });
        
        console.log('Rendering', words.length, 'words on canvas', this.canvas.width, 'x', this.canvas.height);
        
        // Clear any existing cloud
        if (this.cloudInstance) {
            this.cloudInstance = null;
        }
        
        // Clear canvas with NO MARGINS
        const ctx = this.canvas.getContext('2d');
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // CRITICAL: Override wordcloud2's internal margin calculation
        // We do this by setting a custom shape that forces words to the edges
        
        const options = {
            ...this.options,
            list: words,
            
            // Force grid size for precise placement
            gridSize: 6, // Smaller grid = more precise
            
            // Aggressive weight factor to fill space
            weightFactor: (weight) => {
                // Dynamic scaling based on canvas size
                const baseSize = Math.min(this.canvas.width, this.canvas.height) * 0.08;
                return weight * baseSize;
            },
            
            // Move origin up to eliminate top margin
            origin: [0.5, 0.2], // Even higher to kill top whitespace
            
            // Custom shape that pushes words to edges
            shape: (theta) => {
                // Make shape fill the entire top portion
                const r = 0.98; // Almost full radius
                
                // Bottom gets slightly flattened for trunk
                if (theta > 2.0 && theta < 4.2) {
                    return r * 0.82;
                }
                return r;
            },
            
            // Disable any built-in padding
            shuffle: false,
            rotateRatio: 0.3,
            weightMode: 'size',
            clearCanvas: true,
            backgroundColor: 'transparent',
            
            // Prevent any automatic margin calculation
            ellipticity: 1.0,
            minSize: 12
        };
        
        // Render the wordcloud
        try {
            this.hideLoading();
            console.log('Rendering WordCloud with FORCE FILL options');
            this.cloudInstance = window.WordCloud(this.canvas, options);
            
            // After rendering, check if we need to scale up
            setTimeout(() => {
                this.scaleUpIfNeeded();
            }, 100);
            
            console.log('WordCloud rendered successfully');
        } catch (e) {
            console.error('Error rendering wordcloud:', e);
            this.showError('Failed to render word cloud: ' + e.message);
        }
    }
    
    /**
     * If there's still whitespace, scale up the words
     */
    scaleUpIfNeeded() {
        if (!this.canvas) return;
        
        const ctx = this.canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const data = imageData.data;
        
        // Check if top 10% of canvas is empty
        let topEmpty = true;
        for (let y = 0; y < this.canvas.height * 0.1; y++) {
            for (let x = 0; x < this.canvas.width; x += 10) {
                const index = (y * this.canvas.width + x) * 4;
                if (data[index + 3] > 0) { // Has alpha > 0
                    topEmpty = false;
                    break;
                }
            }
            if (!topEmpty) break;
        }
        
        // If top is empty, re-render with even higher origin
        if (topEmpty && this.wordData.words.length > 0) {
            console.log('Top area empty, re-rendering with higher origin');
            this.options.origin = [0.5, 0.15];
            
            // Re-render
            const words = this.wordData.words.map(item => [item.word, item.weight]);
            const options = {
                ...this.options,
                list: words,
                clearCanvas: true
            };
            
            try {
                this.cloudInstance = window.WordCloud(this.canvas, options);
            } catch (e) {
                console.error('Error in scale-up render:', e);
            }
        }
    }
    
    showEmptyState() {
        if (!this.canvas) return;
        
        const ctx = this.canvas.getContext('2d');
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw an empty tree that fills the space
        this.drawEmptyTree(ctx);
        
        if (this.wordCountEl) {
            this.wordCountEl.textContent = '0';
        }
    }
    
    drawEmptyTree(ctx) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        ctx.save();
        
        // Tree crown - positioned to fill the space
        ctx.beginPath();
        ctx.ellipse(width/2, height * 0.3, width * 0.4, height * 0.3, 0, 0, Math.PI * 2);
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 8]);
        ctx.stroke();
        
        // Trunk connection point
        ctx.beginPath();
        ctx.moveTo(width/2, height * 0.5);
        ctx.lineTo(width/2, height * 0.8);
        ctx.stroke();
        
        // Text
        ctx.setLineDash([]);
        ctx.font = '24px system-ui, sans-serif';
        ctx.fillStyle = '#6c757d';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No words shared yet', width / 2, height * 0.35);
        
        ctx.restore();
    }
    
    getWordColor(word, weight) {
        // Rich green colors for the tree leaves
        const greenColors = [
            '#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#4CAF50', 
            '#66BB6A', '#81C784', '#A5D6A7', '#0B5E1B', '#137333',
            '#1E7E34', '#2E8B57', '#228B22', '#32CD32', '#006400'
        ];
        
        // Use the word to choose a consistent color
        const hash = word.split('').reduce((acc, char) => {
            return ((acc << 5) - acc) + char.charCodeAt(0);
        }, 0);
        
        return greenColors[Math.abs(hash) % greenColors.length];
    }
    
    setupFilterControls() {
        const filterContainer = document.getElementById(`filters-${this.containerId}`);
        if (!filterContainer) return;
        
        const dateItems = filterContainer.querySelectorAll('.dropdown-item[href*="date_filter"]');
        dateItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const url = new URL(item.href, window.location.origin);
                const dateFilter = url.searchParams.get('date_filter');
                this.applyFilter('date', dateFilter);
            });
        });
        
        const activityItems = filterContainer.querySelectorAll('.dropdown-item[href*="activity_filter"]');
        activityItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const url = new URL(item.href, window.location.origin);
                const activityFilter = url.searchParams.get('activity_filter');
                this.applyFilter('activity', activityFilter);
            });
        });
    }
    
    applyFilter(type, value) {
        const url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);
        params.set(type + '_filter', value);
        
        let newUrl = url.pathname;
        const paramString = params.toString();
        if (paramString) {
            newUrl += '?' + paramString;
        }
        
        window.location.href = newUrl;
    }
    
    handleWordClick(word) {
        const params = this.getFilterParams();
        const event = new CustomEvent('wordtree:wordclick', {
            detail: { 
                word, 
                containerId: this.containerId,
                filters: params
            }
        });
        this.container.dispatchEvent(event);
        
        if (this.options.onWordClick) {
            this.options.onWordClick(word, params);
        }
    }
    
    getFilterParams() {
        const params = new URLSearchParams(window.location.search);
        const parts = [];
        if (params.has('date_filter')) {
            parts.push(`date_filter=${params.get('date_filter')}`);
        }
        if (params.has('activity_filter')) {
            parts.push(`activity_filter=${params.get('activity_filter')}`);
        }
        return parts.join('&');
    }
    
    setupEventListeners() {
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    handleResize() {
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            this.forceCanvasSize();
            this.render();
        }, 250);
    }
    
    showLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.remove('d-none');
        }
    }
    
    hideLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.add('d-none');
        }
    }
    
    showError(message) {
        if (this.errorEl) {
            const messageEl = this.errorEl.querySelector('.error-message');
            if (messageEl) {
                messageEl.textContent = message || 'Failed to load word tree data.';
            }
            this.errorEl.classList.remove('d-none');
            
            setTimeout(() => {
                this.errorEl.classList.add('d-none');
            }, 5000);
        }
    }
    
    updateWordCount(count) {
        if (this.wordCountEl) {
            this.wordCountEl.textContent = count;
        }
    }
    
    destroy() {
        if (this.cloudInstance) {
            this.cloudInstance = null;
        }
        window.removeEventListener('resize', this.handleResize.bind(this));
    }
}

// Expose WordTree globally
if (typeof window !== 'undefined') {
    window.WordTree = WordTree;
    console.log('WordTree class exported to window with FORCE FILL enabled');
}