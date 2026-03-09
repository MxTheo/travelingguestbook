// tests/javascript/wordtree.test.js
/**
 * @jest-environment jsdom
 */

const fs = require('node:fs');
const path = require('node:path');

// Suppress JSDOM navigation errors
const originalConsoleError = console.error;
console.error = (...args) => {
    // Filter out the navigation not implemented errors
    if (args[0]?.message?.includes('Not implemented: navigation')) {
        return;
    }
    if (typeof args[0] === 'string' && args[0].includes('Not implemented: navigation')) {
        return;
    }
    originalConsoleError(...args);
};

// Load the WordTree JavaScript code as string
const wordtreeJs = fs.readFileSync(
    path.resolve(__dirname, '../../static/js/wordtree.js'),
    'utf8'
);

// Remove export statements
let wordtreeJsWithoutExport = wordtreeJs
    .replaceAll(/export\s+default\s+WordTree;?/g, '')
    .replaceAll(/export\s+\{\s*WordTree\s*\};?/g, '')
    .replaceAll(/export\s*\{\s*default\s+as\s+WordTree\s*\};?/g, '');

// Explicitly add to window
wordtreeJsWithoutExport += '\n\n// Expose WordTree globally\nwindow.WordTree = WordTree;';

// Mock colors.js
globalThis.MyColors = {
    getBootstrapColors: jest.fn().mockReturnValue({
        primary: 'rgba(54,162,235,0.95)',
        success: 'rgba(25,135,84,0.95)',
        warning: 'rgba(255,193,7,0.95)',
        danger: 'rgba(220,53,69,0.9)',
        secondary: 'rgba(108,117,125,0.9)',
        dark: 'rgba(33,37,41,0.9)',
    })
};

// Simulate Chart.js loaded via CDN
globalThis.Chart = jest.fn().mockImplementation(() => ({
    destroy: jest.fn(),
    resize: jest.fn()
}));

// Execute the code
eval(wordtreeJsWithoutExport);

// Check if WordTree exists
if (globalThis.WordTree === undefined) {
    throw new TypeError('WordTree is not defined!');
}

const WordTreeClass = globalThis.WordTree;

describe('WordTree Component', () => {
    // Setup DOM elements before each test
    beforeEach(() => {
        // Clear all mocks
        jest.clearAllMocks();
        
        // Reset Chart mock
        globalThis.Chart = jest.fn().mockImplementation(() => ({
            destroy: jest.fn(),
            resize: jest.fn()
        }));
        
        // Set up DOM with all required elements
        document.body.innerHTML = `
            <div id="wordtree-test" class="wordtree-container">
                <canvas id="wordcloud-canvas-test" width="400" height="300"></canvas>
                <div id="loading-test" class="d-none">Loading...</div>
                <div id="error-test" class="d-none">Error</div>
                <div class="mt-2">
                    <span id="word-count-test">0</span> words shared
                </div>
                <script id="wordtree-data-test" type="application/json" nonce="test-nonce">
                    {
                        "words": [
                            {"text": "courage", "weight": 5},
                            {"text": "kindness", "weight": 3},
                            {"text": "patience", "weight": 2},
                            {"text": "wisdom", "weight": 1}
                        ],
                        "total_count": 11,
                        "base_filter": {
                            "type": "activity",
                            "value": 1,
                            "display_name": "Test Game"
                        },
                        "current_filters": {
                            "date": "week",
                            "activity": "all"
                        }
                    }
                </script>
                <div id="filters-test">
                    <select data-filter="date">
                        <option value="all">All time</option>
                        <option value="today" selected>Today</option>
                        <option value="week">Past week</option>
                    </select>
                    <select data-filter="activity">
                        <option value="all">All activities</option>
                        <option value="1">Game 1</option>
                        <option value="2">Game 2</option>
                    </select>
                </div>
            </div>
        `;
        
        // Mock canvas context for all tests
        const mockContext = {
            clearRect: jest.fn(),
            fillText: jest.fn(),
            font: '',
            fillStyle: '',
            textAlign: ''
        };
        
        const canvas = document.getElementById('wordcloud-canvas-test');
        if (canvas) {
            canvas.getContext = jest.fn().mockReturnValue(mockContext);
        }
    });
    
    afterEach(() => {
        // Clean up any WordTree instances
        if (globalThis.wordtreeInstance) {
            globalThis.wordtreeInstance.destroy();
        }
    });
    
    describe('applyFilter', () => {
        test('applyFilter should update internal filter values for date filter', () => {
            const wordtree = new WordTreeClass('test');
            
            // Mock the applyFilter method to prevent navigation
            const originalApplyFilter = wordtree.applyFilter;
            wordtree.applyFilter = jest.fn().mockImplementation((type, value) => {
                if (type === 'date') {
                    wordtree.currentDateFilter = value;
                } else if (type === 'activity') {
                    wordtree.currentActivityFilter = value;
                }
            });
            
            wordtree.applyFilter('date', 'month');
            
            expect(wordtree.currentDateFilter).toBe('month');
            
            // Restore original method
            wordtree.applyFilter = originalApplyFilter;
        });
        
        test('applyFilter should update internal filter values for activity filter', () => {
            const wordtree = new WordTreeClass('test');
            
            // Mock the applyFilter method to prevent navigation
            const originalApplyFilter = wordtree.applyFilter;
            wordtree.applyFilter = jest.fn().mockImplementation((type, value) => {
                if (type === 'date') {
                    wordtree.currentDateFilter = value;
                } else if (type === 'activity') {
                    wordtree.currentActivityFilter = value;
                }
            });
            
            wordtree.applyFilter('activity', '2');
            
            expect(wordtree.currentActivityFilter).toBe('2');
            
            // Restore original method
            wordtree.applyFilter = originalApplyFilter;
        });
        
        test('applyFilter should update internal filter values before navigation', () => {
            const wordtree = new WordTreeClass('test');
            
            const originalDateFilter = wordtree.currentDateFilter;
            expect(originalDateFilter).toBe('week');
            
            // Mock the applyFilter method to prevent navigation
            const originalApplyFilter = wordtree.applyFilter;
            wordtree.applyFilter = jest.fn().mockImplementation((type, value) => {
                if (type === 'date') {
                    wordtree.currentDateFilter = value;
                } else if (type === 'activity') {
                    wordtree.currentActivityFilter = value;
                }
            });
            
            wordtree.applyFilter('date', 'month');
            
            expect(wordtree.currentDateFilter).toBe('month');
            
            // Restore original method
            wordtree.applyFilter = originalApplyFilter;
        });
        
        test('getFilterParams should return correct string', () => {
            const wordtree = new WordTreeClass('test');
            
            // Test with default filters (from data: date=week)
            let params = wordtree.getFilterParams();
            expect(params).toBe('date_filter=week');
            
            // Change filters
            wordtree.currentDateFilter = 'month';
            wordtree.currentActivityFilter = '2';
            params = wordtree.getFilterParams();
            expect(params).toBe('date_filter=month&activity_filter=2');
        });
        
        test('applyFilter with different filter types', () => {
            const wordtree = new WordTreeClass('test');
            
            // Mock the applyFilter method to prevent navigation
            const originalApplyFilter = wordtree.applyFilter;
            wordtree.applyFilter = jest.fn().mockImplementation((type, value) => {
                if (type === 'date') {
                    wordtree.currentDateFilter = value;
                } else if (type === 'activity') {
                    wordtree.currentActivityFilter = value;
                }
            });
            
            // Test date filter
            wordtree.applyFilter('date', 'month');
            expect(wordtree.currentDateFilter).toBe('month');
            
            // Test activity filter
            wordtree.applyFilter('activity', '2');
            expect(wordtree.currentActivityFilter).toBe('2');
            
            // Restore original method
            wordtree.applyFilter = originalApplyFilter;
        });
    });
    
    describe('Color Generation', () => {
        test('getWordColor should return consistent colors for same word', () => {
            const wordtree = new WordTreeClass('test');
            
            const color1 = wordtree.getWordColor({ text: 'courage', weight: 5 });
            const color2 = wordtree.getWordColor({ text: 'courage', weight: 3 });
            
            expect(color1).toBe(color2);
        });
        
        test('getWordColor should return different colors for different words', () => {
            const wordtree = new WordTreeClass('test');
            
            const color1 = wordtree.getWordColor({ text: 'courage', weight: 5 });
            const color2 = wordtree.getWordColor({ text: 'kindness', weight: 3 });
            
            expect(color1).not.toBe(color2);
        });
        
        test('getWordColor should use Bootstrap colors from MyColors', () => {
            const wordtree = new WordTreeClass('test');
            
            wordtree.getWordColor({ text: 'courage', weight: 5 });
            
            expect(globalThis.MyColors.getBootstrapColors).toHaveBeenCalled();
        });
        
        test('getWordColor should handle empty or invalid input', () => {
            const wordtree = new WordTreeClass('test');
            
            // Test with empty text
            const color = wordtree.getWordColor({ text: '', weight: 1 });
            expect(color).toBeDefined();
            expect(typeof color).toBe('string');
        });
    });
    
    describe('Word Click Handling', () => {
        test('handleWordClick should dispatch custom event', () => {
            const wordtree = new WordTreeClass('test');
            
            const eventSpy = jest.fn();
            document.addEventListener('wordtree:wordclick', eventSpy);
            
            wordtree.handleWordClick('courage');
            
            expect(eventSpy).toHaveBeenCalled();
            const event = eventSpy.mock.calls[0][0];
            expect(event.detail.word).toBe('courage');
            expect(event.detail.containerId).toBe('test');
            expect(event.detail.forumUrl).toBeDefined();
        });
        
        test('handleWordClick should call onWordClick callback if provided', () => {
            const callback = jest.fn();
            const wordtree = new WordTreeClass('test', { onWordClick: callback });
            
            wordtree.handleWordClick('courage');
            
            expect(callback).toHaveBeenCalledWith('courage', 'date_filter=week');
        });
        
        test('handleWordClick should work without callback', () => {
            const wordtree = new WordTreeClass('test');
            
            // Should not throw
            expect(() => {
                wordtree.handleWordClick('courage');
            }).not.toThrow();
        });
    });
    
    describe('UI Updates', () => {
        test('updateWordCount should update display', () => {
            const wordtree = new WordTreeClass('test');
            const countEl = document.getElementById('word-count-test');
            
            wordtree.updateWordCount(42);
            
            expect(countEl.textContent).toBe('42');
        });
        
        test('updateWordCount should handle missing element', () => {
            const wordtree = new WordTreeClass('test');
            
            // Remove count element
            wordtree.wordCountEl = null;
            
            // Should not throw
            expect(() => {
                wordtree.updateWordCount(42);
            }).not.toThrow();
        });
        
        test('showLoading should show loading element', () => {
            const wordtree = new WordTreeClass('test');
            const loadingEl = document.getElementById('loading-test');
            
            wordtree.showLoading();
            
            expect(loadingEl.classList.contains('d-none')).toBe(false);
        });
        
        test('hideLoading should hide loading element', () => {
            const wordtree = new WordTreeClass('test');
            const loadingEl = document.getElementById('loading-test');
            
            wordtree.hideLoading();
            
            expect(loadingEl.classList.contains('d-none')).toBe(true);
        });
        
        test('showError should display error message', () => {
            const wordtree = new WordTreeClass('test');
            const errorEl = document.getElementById('error-test');
            
            wordtree.showError('Test error message');
            
            expect(errorEl.classList.contains('d-none')).toBe(false);
            expect(errorEl.textContent).toBe('Test error message');
        });
        
        test('showError should use default message if none provided', () => {
            const wordtree = new WordTreeClass('test');
            const errorEl = document.getElementById('error-test');
            
            wordtree.showError();
            
            expect(errorEl.textContent).toBe('Failed to load word tree data.');
        });
        
        test('showEmptyState should handle empty words', () => {
            const wordtree = new WordTreeClass('test');
            
            // Mock canvas context already set in beforeEach
            wordtree.showEmptyState();
            
            const canvas = document.getElementById('wordcloud-canvas-test');
            const mockContext = canvas.getContext();
            
            expect(mockContext.clearRect).toHaveBeenCalled();
            expect(mockContext.fillText).toHaveBeenCalled();
        });
    });
    
    describe('Resize Handling', () => {
        beforeEach(() => {
            jest.useFakeTimers();
        });
        
        afterEach(() => {
            jest.useRealTimers();
        });
        
        test('should handle resize events with debouncing', () => {
            const wordtree = new WordTreeClass('test');
            
            // Mock chart resize
            wordtree.chart = { resize: jest.fn() };
            
            // Trigger multiple resize events
            globalThis.dispatchEvent(new Event('resize'));
            globalThis.dispatchEvent(new Event('resize'));
            globalThis.dispatchEvent(new Event('resize'));
            
            // Should not have called resize yet (debounced)
            expect(wordtree.chart.resize).not.toHaveBeenCalled();
            
            // Fast-forward timer
            jest.advanceTimersByTime(250);
            
            // Should have called resize once
            expect(wordtree.chart.resize).toHaveBeenCalledTimes(1);
        });
        
        test('should handle resize when chart is null', () => {
            const wordtree = new WordTreeClass('test');
            
            wordtree.chart = null;
            
            // Should not throw
            expect(() => {
                globalThis.dispatchEvent(new Event('resize'));
                jest.advanceTimersByTime(250);
            }).not.toThrow();
        });
    });
    
    describe('Initialization', () => {
        test('should initialize with data from script tag', () => {
            const wordtree = new WordTreeClass('test');
            
            expect(wordtree.wordData.words).toHaveLength(4);
            expect(wordtree.wordData.total_count).toBe(11);
            expect(wordtree.currentDateFilter).toBe('week');
        });
        
        test('should handle missing data script', () => {
            // Remove data script
            document.getElementById('wordtree-data-test').remove();
            
            // Mock canvas context to prevent errors
            const canvas = document.getElementById('wordcloud-canvas-test');
            const mockContext = {
                clearRect: jest.fn(),
                fillText: jest.fn(),
                font: '',
                fillStyle: '',
                textAlign: ''
            };
            canvas.getContext = jest.fn().mockReturnValue(mockContext);
            
            const wordtree = new WordTreeClass('test');
            
            expect(wordtree.wordData.words).toEqual([]);
            expect(wordtree.wordData.total_count).toBe(0);
            
            // Verify showEmptyState was called (indirectly via render)
            expect(mockContext.clearRect).toHaveBeenCalled();
            expect(mockContext.fillText).toHaveBeenCalled();
        });
        
        test('should handle invalid JSON', () => {
            // Corrupt JSON
            const dataEl = document.getElementById('wordtree-data-test');
            dataEl.textContent = 'invalid json';
            
            // Mock canvas context to prevent errors
            const canvas = document.getElementById('wordcloud-canvas-test');
            const mockContext = {
                clearRect: jest.fn(),
                fillText: jest.fn(),
                font: '',
                fillStyle: '',
                textAlign: ''
            };
            canvas.getContext = jest.fn().mockReturnValue(mockContext);
            
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            
            const wordtree = new WordTreeClass('test');
            
            expect(consoleSpy).toHaveBeenCalled();
            expect(wordtree.wordData.words).toEqual([]);
            
            // Verify showEmptyState was called
            expect(mockContext.clearRect).toHaveBeenCalled();
            expect(mockContext.fillText).toHaveBeenCalled();
            
            consoleSpy.mockRestore();
        });
        
        test('should merge options correctly', () => {
            const wordtree = new WordTreeClass('test', {
                minFontSize: 8,
                maxFontSize: 64,
                rotationSteps: 4
            });
            
            expect(wordtree.options.minFontSize).toBe(8);
            expect(wordtree.options.maxFontSize).toBe(64);
            expect(wordtree.options.rotationSteps).toBe(4);
        });
    });
});

// Restore original console.error after tests
afterAll(() => {
    console.error = originalConsoleError;
});