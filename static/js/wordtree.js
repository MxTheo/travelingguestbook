// static/js/wordtree.js
/**
 * WordTree Component
 * 
 * A reusable word cloud visualization that displays words as leaves on a tree.
 * Words are rendered using Chart.js word cloud plugin with sizes based on frequency.
 * 
 * Features:
 * - Progressive filtering (date, activity)
 * - Clickable words (for future forum integration)
 * - Responsive design
 * - Uses Bootstrap colors for consistency
 * 
 * @class WordTree
 */

class WordTree {
    /**
     * Create a new WordTree instance
     * 
     * @param {string} containerId - Unique ID for this word tree instance (without 'wordtree-' prefix)
     * @param {Object} options - Configuration options
     * @param {number} options.minFontSize - Minimum font size for words (default: 12)
     * @param {number} options.maxFontSize - Maximum font size for words (default: 48)
     * @param {number} options.rotationSteps - Number of rotation steps (0, 90, etc.) (default: 2)
     * @param {number} options.rotationProbability - Chance of word rotation (default: 0.3)
     * @param {Function} options.onWordClick - Callback when word is clicked
     */
    constructor(containerId, options = {}) {
        // Store container ID and find the DOM element
        this.containerId = containerId;
        this.container = document.getElementById(`wordtree-${containerId}`);
        
        // Exit if container doesn't exist (prevents errors on pages without word tree)
        if (!this.container) {
            console.warn(`WordTree container #wordtree-${containerId} not found`);
            return;
        }

        // Find all required DOM elements
        this.canvas = document.getElementById(`wordcloud-canvas-${containerId}`);
        this.loadingEl = document.getElementById(`loading-${containerId}`);
        this.errorEl = document.getElementById(`error-${containerId}`);
        this.wordCountEl = document.getElementById(`word-count-${containerId}`);
        
        // Get initial data from embedded JSON (set by Django template)
        const dataElement = document.getElementById(`wordtree-data-${containerId}`);
        if (dataElement) {
            try {
                this.wordData = JSON.parse(dataElement.textContent);
            } catch (e) {
                console.error('Failed to parse word tree data:', e);
                this.wordData = { words: [], total_count: 0, base_filter: {}, current_filters: {} };
            }
        } else {
            this.wordData = { words: [], total_count: 0, base_filter: {}, current_filters: {} };
        }
        
        // Extract filter information from the data
        this.baseFilter = this.wordData.base_filter || { type: 'all', value: '', display_name: 'All words' };
        this.currentDateFilter = this.wordData.current_filters?.date || 'all';
        this.currentActivityFilter = this.wordData.current_filters?.activity || 'all';
        
        // Merge default options with user-provided options
        this.options = {
            minFontSize: 12,
            maxFontSize: 48,
            rotationSteps: 2,        // 0° and 90° rotation for zen-like simplicity
            rotationProbability: 0.3, // 30% chance of rotation
            ...options
        };
        
        // Chart.js instance (will be created in render())
        this.chart = null;
        
        // Debounce timeout for resize events
        this.resizeTimeout = null;
        
        // Initialize the component
        this.init();
    }
    
    /**
     * Initialize the word tree component
     * Sets up rendering and event listeners
     * 
     * @private
     */
    init() {
        this.render();
        this.setupEventListeners();
        this.setupFilterControls();
    }
    
    /**
     * Render the word cloud using Chart.js word cloud plugin
     * 
     * The word cloud plugin expects:
     * - labels: array of words
     * - data: array of weights (frequencies)
     * - color: array of colors for each word
     * 
     * @private
     */
    render() {
        // Don't render if canvas doesn't exist or no words to display
        if (!this.canvas || !this.wordData.words || this.wordData.words.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Prepare data for Chart.js word cloud
        const wordData = this.wordData.words.map(word => ({
            word: word.text,
            weight: word.weight || 1,
            color: this.getWordColor(word)
        }));
        
        // Destroy existing chart if it exists (prevents memory leaks)
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Create new word cloud chart
        // Chart.js word cloud plugin registers the 'wordCloud' chart type
        this.chart = new Chart(this.canvas, {
            type: 'wordCloud',
            data: {
                labels: wordData.map(w => w.word),
                datasets: [{
                    label: 'Word frequency',
                    data: wordData.map(w => w.weight),
                    color: wordData.map(w => w.color)
                }]
            },
            options: {
                plugins: {
                    // Hide the legend (not needed for word cloud)
                    legend: { display: false },
                    
                    // Customize tooltips that appear on hover
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const word = wordData[context.dataIndex];
                                return `${word.word}: ${word.weight} occurrence${word.weight === 1 ? '' : 's'}`;
                            }
                        }
                    }
                },
                elements: {
                    word: {
                        padding: 5,           // Space between words
                        minFontSize: this.options.minFontSize,
                        maxFontSize: this.options.maxFontSize,
                        rotation: this.options.rotationSteps,
                        rotationProbability: this.options.rotationProbability
                    }
                },
                // Handle word click events
                onClick: (event, elements) => {
                    if (elements && elements.length > 0) {
                        const index = elements[0].index;
                        const word = wordData[index];
                        this.handleWordClick(word.word);
                    }
                }
            }
        });
        
        // Update the word count display
        this.updateWordCount(this.wordData.total_count);
    }
    
    /**
     * Show empty state when no words are available
     * 
     * @private
     */
    showEmptyState() {
        // Clear the canvas
        const ctx = this.canvas.getContext('2d');
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw a friendly message
        ctx.font = '16px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
        ctx.fillStyle = 'var(--bs-secondary)';
        ctx.textAlign = 'center';
        ctx.fillText('Nog geen woorden gedeeld', this.canvas.width / 2, this.canvas.height / 2);
        
        this.updateWordCount(0);
    }
    
    /**
     * Set up filter controls (dropdowns) and attach event listeners
     * 
     * @private
     */
    setupFilterControls() {
        const filterContainer = document.getElementById(`filters-${this.containerId}`);
        if (!filterContainer) return;
        
        // Date filter dropdown
        const dateFilter = filterContainer.querySelector('[data-filter="date"]');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.applyFilter('date', e.target.value);
            });
        }
        
        // Activity filter dropdown (if it exists)
        const activityFilter = filterContainer.querySelector('[data-filter="activity"]');
        if (activityFilter) {
            activityFilter.addEventListener('change', (e) => {
                this.applyFilter('activity', e.target.value);
            });
        }
    }
    
    /**
     * Apply a filter and reload the page with new parameters
     * 
     * This uses page reload instead of AJAX because:
     * 1. Simpler implementation for MVP
     * 2. SEO-friendly (filters in URL)
     * 3. Shareable URLs
     * 
     * @param {string} filterType - Type of filter ('date' or 'activity')
     * @param {string} filterValue - New filter value
     */
    applyFilter(filterType, filterValue) {
        const url = new URL(globalThis.location.href);
        const params = new URLSearchParams(url.search);
        
        if (filterType === 'date') {
            params.set('date_filter', filterValue);
            this.currentDateFilter = filterValue;
        } else if (filterType === 'activity') {
            params.set('activity_filter', filterValue);
            this.currentActivityFilter = filterValue;
        }
        
        // Reload page with new filters
        globalThis.location.href = `${url.pathname}?${params.toString()}`;
    }
    
    /**
     * Get color for a word based on its text (consistent hashing)
     * 
     * Uses a simple string hash to ensure the same word always gets the same color.
     * This creates visual consistency across page loads.
     * 
     * @param {Object} word - Word object with text and weight
     * @returns {string} CSS color value (rgba format)
     */
    getWordColor(word) {
        // Get Bootstrap colors from global MyColors object
        const colors = globalThis.MyColors?.getBootstrapColors() || {
            primary: 'rgba(54,162,235,0.95)',
            success: 'rgba(25,135,84,0.95)',
            warning: 'rgba(255,193,7,0.95)',
            danger: 'rgba(220,53,69,0.9)',
            secondary: 'rgba(108,117,125,0.9)',
        };
        
        // Convert colors object to array for easy access
        const colorArray = Object.values(colors);
        
        /**
         * Simple string hash function (djb2 algorithm)
         * 
         * Why djb2?
         * - Simple and fast
         * - Good distribution for short strings (like our words)
         * - Deterministic: same input always produces same output
         * 
         * Algorithm: hash = hash * 33 + charCode
         * 33 is used because it works well with ASCII characters
         */
        const hash = word.text.split('').reduce((acc, char) => {
            // Multiply by 33 (using shift + add for speed)
            // Then add character code
            return ((acc << 5) - acc) + char.codePointAt(0);
        }, 0);
        
        // Use absolute value to handle negative hashes
        // Modulo to stay within array bounds
        const colorIndex = Math.abs(hash) % colorArray.length;
        
        return colorArray[colorIndex];
    }
    
    /**
     * Handle word click events
     * 
     * Dispatches a custom event that other parts of the application can listen for.
     * This is designed for future forum integration - when a word is clicked,
     * we can navigate to a forum thread about that word.
     * 
     * @param {string} word - The clicked word
     */
    handleWordClick(word) {
        // Create a custom event with detailed information about the click
        const event = new CustomEvent('wordtree:wordclick', {
            detail: {
                word: word,
                containerId: this.containerId,
                filters: {
                    base: this.baseFilter,
                    date: this.currentDateFilter,
                    activity: this.currentActivityFilter
                },
                // Generate URL for potential navigation (for future use)
                forumUrl: `/forum/word/${encodeURIComponent(word)}/?${this.getFilterParams()}`
            },
            // Allow the event to bubble up the DOM tree
            bubbles: true
        });
        
        // Dispatch the event from the container
        this.container.dispatchEvent(event);
        
        // If a callback was provided in options, call it
        if (this.options.onWordClick) {
            this.options.onWordClick(word, this.getFilterParams());
        }
    }
    
    /**
     * Get current filter parameters as URL string
     * 
     * @returns {string} URL query string (e.g., "date_filter=week&activity_filter=1")
     */
    getFilterParams() {
        const params = new URLSearchParams();
        if (this.currentDateFilter !== 'all') {
            params.set('date_filter', this.currentDateFilter);
        }
        if (this.currentActivityFilter !== 'all') {
            params.set('activity_filter', this.currentActivityFilter);
        }
        return params.toString();
    }
    
    /**
     * Update the word count display with animation
     * 
     * @param {number} count - Total number of words
     */
    updateWordCount(count) {
        if (this.wordCountEl) {
            this.wordCountEl.textContent = count;
            
            // Add animation class for visual feedback
            this.wordCountEl.classList.add('word-count-update');
            
            // Remove animation class after it completes
            setTimeout(() => {
                this.wordCountEl.classList.remove('word-count-update');
            }, 300);
        }
    }
    
    /**
     * Setup global event listeners
     * 
     * @private
     */
    setupEventListeners() {
        // Handle window resize with debouncing
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    /**
     * Handle window resize event
     * 
     * Debounces the resize event to prevent too many chart redraws.
     * Only redraws after the user has stopped resizing for 250ms.
     * 
     * @private
     */
    handleResize() {
        clearTimeout(this.resizeTimeout);
        this.resizeTimeout = setTimeout(() => {
            if (this.chart) {
                this.chart.resize();
            }
        }, 250);
    }
    
    /**
     * Show loading spinner
     * 
     * @private
     */
    showLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.remove('d-none');
        }
        if (this.canvas) {
            this.canvas.style.opacity = '0.5';
        }
    }
    
    /**
     * Hide loading spinner
     * 
     * @private
     */
    hideLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.add('d-none');
        }
        if (this.canvas) {
            this.canvas.style.opacity = '1';
        }
    }
    
    /**
     * Show error message
     * 
     * @param {string} message - Error message to display
     * @private
     */
    showError(message) {
        if (this.errorEl) {
            this.errorEl.textContent = message || 'Failed to load word tree data.';
            this.errorEl.classList.remove('d-none');
        }
    }
    
    /**
     * Clean up resources when component is destroyed
     * 
     * This is important for single-page applications to prevent memory leaks.
     */
    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
        window.removeEventListener('resize', this.handleResize.bind(this));
    }
}

// Auto-initialize all word trees when DOM is loaded
// This allows the component to work without manual initialization
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[id^="wordtree-"]').forEach(container => {
        // Extract containerId from the full ID (remove 'wordtree-' prefix)
        const containerId = container.id.replace('wordtree-', '');
    });
});

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment (for tests)
    module.exports = WordTree;
} else {
    // Browser environment
    globalThis.WordTree = WordTree;
}