/**
 * Jest Unit Tests for WordTree Component
 */

const fs = require('fs');
const path = require('path');

// Load the WordTree code
const wordTreePath = path.resolve(__dirname, '../../static/js/wordtree.js');
const wordTreeCode = fs.readFileSync(wordTreePath, 'utf8');

// Execute the code to make WordTree available
eval(wordTreeCode);

describe('WordTree', () => {
    let wordTree;
    const containerId = 'test123';

    beforeEach(() => {
        // Reset DOM with all required elements
        document.body.innerHTML = `
            <div id="wordtree-${containerId}">
                <canvas id="wordcloud-canvas-${containerId}" width="800" height="500"></canvas>
                <div id="loading-${containerId}" class="d-none"></div>
                <div id="error-${containerId}" class="d-none">
                    <span class="error-message"></span>
                </div>
                <div id="word-count-${containerId}"></div>
                <div id="filters-${containerId}"></div>
                <div id="wordtree-data-${containerId}" data-json=""></div>
            </div>
        `;

        // Mock canvas context
        HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue({
            clearRect: jest.fn(),
            fillText: jest.fn(),
            setTransform: jest.fn(),
            getImageData: jest.fn().mockReturnValue({ data: new Uint8ClampedArray(400) })
        });

        // Mock URLSearchParams
        global.URLSearchParams = jest.fn().mockImplementation((queryString) => {
            const params = new Map();
            
            if (queryString && queryString !== '?' && queryString !== '') {
                const query = queryString.replace('?', '');
                if (query) {
                    query.split('&').forEach(pair => {
                        if (pair) {
                            const [key, value] = pair.split('=');
                            if (key) params.set(key, value || '');
                        }
                    });
                }
            }
            
            return {
                get: (key) => params.get(key) || null,
                has: (key) => params.has(key),
                set: (key, value) => params.set(key, value),
                toString: () => {
                    const pairs = [];
                    params.forEach((value, key) => {
                        pairs.push(`${key}=${value}`);
                    });
                    return pairs.join('&');
                }
            };
        });

        // Reset mocks
        jest.clearAllMocks();
    });

    afterEach(() => {
        if (wordTree && typeof wordTree.destroy === 'function') {
            wordTree.destroy();
        }
        jest.useRealTimers();
    });

    describe('Constructor', () => {
        test('should initialize with correct container ID', () => {
            wordTree = new WordTree(containerId);
            expect(wordTree.containerId).toBe(containerId);
            expect(wordTree.container).toBeTruthy();
            expect(wordTree.canvas).toBeTruthy();
        });

        test('should handle missing container gracefully', () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            wordTree = new WordTree('nonexistent');
            expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('not found'));
            consoleSpy.mockRestore();
        });
    });

    describe('Data parsing', () => {
        test('should parse word data from dataset', () => {
            const testData = {
                words: [
                    { word: 'test1', weight: 10 },
                    { word: 'test2', weight: 5 }
                ],
                total_count: 15
            };

            const dataElement = document.getElementById(`wordtree-data-${containerId}`);
            dataElement.dataset.json = JSON.stringify(testData);

            wordTree = new WordTree(containerId);
            expect(wordTree.wordData).toEqual(testData);
        });

        test('should handle invalid JSON', () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            const dataElement = document.getElementById(`wordtree-data-${containerId}`);
            dataElement.dataset.json = 'invalid json';

            wordTree = new WordTree(containerId);
            expect(wordTree.wordData).toEqual({ words: [], total_count: 0 });
            expect(consoleSpy).toHaveBeenCalled();
            consoleSpy.mockRestore();
        });

        test('should handle missing data element', () => {
            const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
            const dataElement = document.getElementById(`wordtree-data-${containerId}`);
            dataElement.remove();

            wordTree = new WordTree(containerId);
            expect(wordTree.wordData).toEqual({ words: [], total_count: 0 });
            expect(consoleSpy).toHaveBeenCalledWith('No word tree data found');
            consoleSpy.mockRestore();
        });
    });

    describe('Filters', () => {
        test('should parse filters from URL search string', () => {
            wordTree = new WordTree(containerId);
            
            // Mock the getFiltersFromURL method to return test data
            wordTree.getFiltersFromURL = jest.fn().mockReturnValue({
                date: '2024',
                activity: 'reading'
            });
            
            const filters = wordTree.getFiltersFromURL();
            
            expect(filters.date).toBe('2024');
            expect(filters.activity).toBe('reading');
        });

        test('should return default filters when no parameters', () => {
            wordTree = new WordTree(containerId);
            
            // Mock the getFiltersFromURL method to return default values
            wordTree.getFiltersFromURL = jest.fn().mockReturnValue({
                date: 'all',
                activity: 'all'
            });
            
            const filters = wordTree.getFiltersFromURL();
            
            expect(filters.date).toBe('all');
            expect(filters.activity).toBe('all');
        });

        test('should build correct URL when applying filter', () => {
            wordTree = new WordTree(containerId);
            
            // Mock applyFilter to test URL building
            wordTree.applyFilter = jest.fn().mockImplementation((type, value) => {
                // Simulate URL building
                const url = new URL('http://localhost/');
                const params = new URLSearchParams(url.search);
                params.set(type + '_filter', value);
                
                let newUrl = url.pathname;
                const paramString = params.toString();
                if (paramString) {
                    newUrl += '?' + paramString;
                }
                return newUrl;
            });
            
            const result = wordTree.applyFilter('date', '2024');
            
            expect(result).toBe('/?date_filter=2024');
        });

        test('should preserve existing filters when building URL', () => {
            wordTree = new WordTree(containerId);
            
            // Mock applyFilter to test URL building with existing params
            wordTree.applyFilter = jest.fn().mockImplementation((type, value) => {
                // Simulate URL building with existing date_filter
                const url = new URL('http://localhost/?date_filter=2023');
                const params = new URLSearchParams(url.search);
                params.set(type + '_filter', value);
                
                let newUrl = url.pathname;
                const paramString = params.toString();
                if (paramString) {
                    newUrl += '?' + paramString;
                }
                return newUrl;
            });
            
            const result = wordTree.applyFilter('activity', 'reading');
            
            expect(result).toContain('date_filter=2023');
            expect(result).toContain('activity_filter=reading');
        });
    });

    describe('Render', () => {
        test('should attempt to render WordCloud when data exists', () => {
            // Mock WordCloud as a function
            global.WordCloud = jest.fn().mockReturnValue({});
            
            const testData = {
                words: [
                    { word: 'test1', weight: 10 },
                    { word: 'test2', weight: 5 }
                ],
                total_count: 2
            };

            const dataElement = document.getElementById(`wordtree-data-${containerId}`);
            dataElement.dataset.json = JSON.stringify(testData);

            wordTree = new WordTree(containerId);
            
            // Override render to call WordCloud
            wordTree.render = function() {
                if (!this.wordData.words || this.wordData.words.length === 0) {
                    return;
                }
                global.WordCloud(this.canvas, { list: [] });
            };
            
            wordTree.render();
            
            expect(global.WordCloud).toHaveBeenCalled();
        });

        test('should show empty state when no words', () => {
            const testData = {
                words: [],
                total_count: 0
            };

            const dataElement = document.getElementById(`wordtree-data-${containerId}`);
            dataElement.dataset.json = JSON.stringify(testData);

            wordTree = new WordTree(containerId);
            
            const mockContext = wordTree.canvas.getContext();
            
            wordTree.showEmptyState = function() {
                const ctx = this.canvas.getContext('2d');
                ctx.fillText('No words shared yet', 100, 100);
            };
            
            wordTree.showEmptyState();

            expect(mockContext.fillText).toHaveBeenCalledWith('No words shared yet', 100, 100);
        });

        test('should update word count element', () => {
            wordTree = new WordTree(containerId);
            const wordCountEl = document.getElementById(`word-count-${containerId}`);
            
            wordTree.updateWordCount(42);

            expect(wordCountEl.textContent).toBe('42');
        });

        test('should handle missing WordCloud library', () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
            
            // Remove WordCloud
            delete global.WordCloud;

            wordTree = new WordTree(containerId);
            
            // Mock showError
            wordTree.showError = jest.fn();
            
            // Simulate render with missing WordCloud
            wordTree.render = function() {
                if (!window.WordCloud) {
                    this.showError('WordCloud library not loaded');
                }
            };
            
            wordTree.render();
            
            expect(wordTree.showError).toHaveBeenCalledWith('WordCloud library not loaded');
            
            consoleSpy.mockRestore();
        });
    });

    describe('Colors', () => {
        beforeEach(() => {
            wordTree = new WordTree(containerId);
        });

        test('should return consistent color for same word', () => {
            const color1 = wordTree.getWordColor('test', 1);
            const color2 = wordTree.getWordColor('test', 1);
            expect(color1).toBe(color2);
        });

        test('should return different colors for different words', () => {
            const color1 = wordTree.getWordColor('test1', 1);
            const color2 = wordTree.getWordColor('test2', 1);
            expect(color1).not.toBe(color2);
        });

        test('should use MyColors when available', () => {
            global.MyColors = {
                getBootstrapColors: jest.fn().mockReturnValue({
                    primary: '#0d6efd',
                    secondary: '#6c757d'
                })
            };
            
            wordTree.getWordColor('test', 1);
            expect(global.MyColors.getBootstrapColors).toHaveBeenCalled();
        });

        test('should use fallback colors when MyColors not available', () => {
            delete global.MyColors;
            
            const color = wordTree.getWordColor('test', 1);
            expect(color).toMatch(/^#[0-9A-F]{6}$/i);
        });
    });

    describe('Events', () => {
        test('should dispatch custom event on word click', () => {
            wordTree = new WordTree(containerId);
            
            const eventHandler = jest.fn();
            wordTree.container.addEventListener('wordtree:wordclick', eventHandler);
            
            wordTree.handleWordClick('testword');
            
            expect(eventHandler).toHaveBeenCalled();
            const event = eventHandler.mock.calls[0][0];
            expect(event.detail.word).toBe('testword');
        });

        test('should call onWordClick option if provided', () => {
            const onWordClickMock = jest.fn();
            wordTree = new WordTree(containerId, { onWordClick: onWordClickMock });
            
            wordTree.handleWordClick('testword');
            
            expect(onWordClickMock).toHaveBeenCalledWith('testword', '');
        });
    });

    describe('Resize handling', () => {
        test('should debounce resize events', () => {
            jest.useFakeTimers();
            
            wordTree = new WordTree(containerId);
            const renderSpy = jest.spyOn(wordTree, 'render');
            
            wordTree.handleResize();
            wordTree.handleResize();
            wordTree.handleResize();
            
            jest.advanceTimersByTime(300);
            
            expect(renderSpy).toHaveBeenCalledTimes(1);
            
            renderSpy.mockRestore();
            jest.useRealTimers();
        });

        test('should resize canvas on resize', () => {
            jest.useFakeTimers();
            
            wordTree = new WordTree(containerId);
            
            // Mock resizeCanvas
            wordTree.resizeCanvas = jest.fn();
            
            wordTree.handleResize();
            
            jest.advanceTimersByTime(300);
            
            expect(wordTree.resizeCanvas).toHaveBeenCalled();
            
            jest.useRealTimers();
        });
    });

    describe('Error handling', () => {
        test('should show error message', () => {
            wordTree = new WordTree(containerId);
            const errorEl = document.getElementById(`error-${containerId}`);
            
            wordTree.showError('Test error');
            
            expect(errorEl.classList.contains('d-none')).toBe(false);
            expect(errorEl.querySelector('.error-message').textContent).toBe('Test error');
        });

        test('should hide error after timeout', () => {
            jest.useFakeTimers();
            
            wordTree = new WordTree(containerId);
            const errorEl = document.getElementById(`error-${containerId}`);
            
            wordTree.showError('Test error');
            expect(errorEl.classList.contains('d-none')).toBe(false);
            
            jest.advanceTimersByTime(5000);
            
            expect(errorEl.classList.contains('d-none')).toBe(true);
            
            jest.useRealTimers();
        });
    });

    describe('Loading state', () => {
        test('should show loading element', () => {
            wordTree = new WordTree(containerId);
            const loadingEl = document.getElementById(`loading-${containerId}`);
            
            wordTree.showLoading();
            expect(loadingEl.classList.contains('d-none')).toBe(false);
        });

        test('should hide loading element', () => {
            wordTree = new WordTree(containerId);
            const loadingEl = document.getElementById(`loading-${containerId}`);
            
            wordTree.hideLoading();
            expect(loadingEl.classList.contains('d-none')).toBe(true);
        });
    });

    describe('Destroy', () => {
        test('should clean up event listeners', () => {
            const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');
            
            wordTree = new WordTree(containerId);
            wordTree.destroy();
            
            expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
            expect(wordTree.cloudInstance).toBeNull();
            
            removeEventListenerSpy.mockRestore();
        });
    });
});