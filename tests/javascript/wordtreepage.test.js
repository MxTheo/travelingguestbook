/**
 * Unit Tests for WordTree Component
 * 
 * Deze tests gebruiken de ingebouwde browser APIs.
 * Voer ze uit in een browser context (bijv. via een test HTML pagina).
 */

class WordTreeTestSuite {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    async runAll() {
        console.log('🧪 Running WordTree Test Suite...\n');
        
        await this.testConstructor();
        await this.testDataParsing();
        await this.testEmptyState();
        await this.testColorGeneration();
        await this.testFilterControls();
        await this.testResizeHandler();
        await this.testWordClick();
        
        console.log(`\n📊 Results: ${this.passed} passed, ${this.failed} failed`);
    }

    async testConstructor() {
        this.setupTestDOM();
        
        try {
            const wordtree = new WordTree('test');
            
            if (wordtree.containerId === 'test') {
                console.log('✅ testConstructor: Container ID correctly set');
                this.passed++;
            } else {
                throw new Error('Container ID not set correctly');
            }
            
            if (wordtree.canvas) {
                console.log('✅ testConstructor: Canvas element found');
                this.passed++;
            } else {
                throw new Error('Canvas not found');
            }
            
        } catch (error) {
            console.log('❌ testConstructor:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testDataParsing() {
        this.setupTestDOM();
        
        // Mock data
        const testData = {
            words: [
                { word: 'test1', weight: 10 },
                { word: 'test2', weight: 5 }
            ],
            total_count: 15
        };
        
        const dataElement = document.getElementById('wordtree-data-test');
        dataElement.dataset.json = JSON.stringify(testData);
        
        try {
            const wordtree = new WordTree('test');
            
            if (wordtree.wordData.words.length === 2) {
                console.log('✅ testDataParsing: Word data parsed correctly');
                this.passed++;
            } else {
                throw new Error('Word data not parsed correctly');
            }
            
            if (wordtree.wordData.total_count === 15) {
                console.log('✅ testDataParsing: Total count parsed correctly');
                this.passed++;
            } else {
                throw new Error('Total count not parsed correctly');
            }
            
        } catch (error) {
            console.log('❌ testDataParsing:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testEmptyState() {
        this.setupTestDOM();
        
        // Geen data
        const dataElement = document.getElementById('wordtree-data-test');
        dataElement.dataset.json = JSON.stringify({ words: [], total_count: 0 });
        
        try {
            const wordtree = new WordTree('test');
            wordtree.render();
            
            const ctx = wordtree.canvas.getContext('2d');
            const canvas = wordtree.canvas;
            
            // Controleer of canvas niet leeg is (empty state text)
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const hasContent = imageData.data.some(value => value !== 0);
            
            if (hasContent) {
                console.log('✅ testEmptyState: Empty state rendered');
                this.passed++;
            } else {
                throw new Error('Empty state not rendered');
            }
            
        } catch (error) {
            console.log('❌ testEmptyState:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testColorGeneration() {
        this.setupTestDOM();
        
        try {
            const wordtree = new WordTree('test');
            
            // Mock MyColors
            window.MyColors = {
                getBootstrapColors: () => ({
                    primary: '#0d6efd',
                    secondary: '#6c757d',
                    success: '#198754'
                })
            };
            
            const color1 = wordtree.getWordColor('test', 1);
            const color2 = wordtree.getWordColor('test', 1); // Zelfde woord = zelfde kleur
            const color3 = wordtree.getWordColor('different', 1);
            
            if (color1 === color2 && color1 !== color3) {
                console.log('✅ testColorGeneration: Colors are consistent');
                this.passed++;
            } else {
                throw new Error('Color generation not consistent');
            }
            
        } catch (error) {
            console.log('❌ testColorGeneration:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testFilterControls() {
        this.setupTestDOM();
        
        try {
            const wordtree = new WordTree('test');
            
            // Test URL parameter parsing
            const originalLocation = window.location;
            delete window.location;
            window.location = new URL('https://test.com?date_filter=2024&activity_filter=reading');
            
            const filters = wordtree.getFiltersFromURL();
            
            if (filters.date === '2024' && filters.activity === 'reading') {
                console.log('✅ testFilterControls: URL parameters parsed correctly');
                this.passed++;
            } else {
                throw new Error('URL parameters not parsed correctly');
            }
            
            window.location = originalLocation;
            
        } catch (error) {
            console.log('❌ testFilterControls:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testResizeHandler() {
        this.setupTestDOM();
        
        try {
            const wordtree = new WordTree('test');
            const originalWidth = wordtree.canvas.width;
            
            // Mock resize
            wordtree.handleResize();
            
            setTimeout(() => {
                try {
                    if (wordtree.resizeTimeout) {
                        console.log('✅ testResizeHandler: Resize handler set timeout');
                        this.passed++;
                    } else {
                        throw new Error('Resize handler not working');
                    }
                } catch (error) {
                    console.log('❌ testResizeHandler:', error.message);
                    this.failed++;
                }
            }, 300);
            
        } catch (error) {
            console.log('❌ testResizeHandler:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    async testWordClick() {
        this.setupTestDOM();
        
        try {
            const wordtree = new WordTree('test', {
                onWordClick: (word, params) => {
                    console.log('Word clicked:', word);
                }
            });
            
            // Test event dispatching
            let eventReceived = false;
            wordtree.container.addEventListener('wordtree:wordclick', () => {
                eventReceived = true;
            });
            
            wordtree.handleWordClick('testword');
            
            if (eventReceived) {
                console.log('✅ testWordClick: Click event dispatched');
                this.passed++;
            } else {
                throw new Error('Click event not dispatched');
            }
            
        } catch (error) {
            console.log('❌ testWordClick:', error.message);
            this.failed++;
        }
        
        this.cleanupTestDOM();
    }

    setupTestDOM() {
        // Create test container
        const container = document.createElement('div');
        container.id = 'wordtree-test';
        container.innerHTML = `
            <canvas id="wordcloud-canvas-test" width="800" height="500"></canvas>
            <div id="loading-test" class="d-none"></div>
            <div id="error-test" class="d-none"><span class="error-message"></span></div>
            <div id="word-count-test"></div>
            <div id="filters-test"></div>
            <div id="wordtree-data-test" data-json=""></div>
        `;
        document.body.appendChild(container);
    }

    cleanupTestDOM() {
        const container = document.getElementById('wordtree-test');
        if (container) {
            container.remove();
        }
    }
}

// Run tests when loaded
if (typeof window !== 'undefined') {
    window.runWordTreeTests = () => {
        const suite = new WordTreeTestSuite();
        suite.runAll();
    };
}