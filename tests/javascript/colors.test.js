// tests/javascript/wordtree.test.js
/**
 * @jest-environment jsdom
 * 
 * These tests test the WordTree class defined in static/js/wordtree.js.
 * We use eval() to load the JavaScript code because the WordTree class
 * is globally available in the browser (via window.WordTree) and not as a module export.
 */

describe('MyColors global', () => {
    beforeAll(() => {
        globalThis.getComputedStyle = jest.fn(() => ({
            getPropertyValue: jest.fn((name) => {
                const map = {
                    '--bs-primary': 'rgba(1,2,3,0.95)',
                    '--bs-danger': 'rgba(4,5,6,0.9)',
                    '--bs-warning': 'rgba(7,8,9,0.95)',
                    '--bs-success': 'rgba(10,11,12,0.95)',
                    '--bs-secondary': 'rgba(13,14,15,0.9)',
                    '--bs-dark': 'rgba(16,17,18,0.9)',
                };
                return map[name] || '';
            }),
        }));

        // Importeer of laad je colors.js zodat window.MyColors bestaat
        // Bijvoorbeeld met jest.mock of require
        require('../../static/js/colors.js');
        // pas pad aan
    });

    test('getBootstrapColors returns correct values', () => {
        const colors = globalThis.MyColors.getBootstrapColors();
        expect(colors.primary).toBe('rgba(1,2,3,0.95)');
        expect(colors.danger).toBe('rgba(4,5,6,0.9)');
    });
});
