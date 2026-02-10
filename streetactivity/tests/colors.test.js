describe('MyColors global', () => {
    beforeAll(() => {
        window.getComputedStyle = jest.fn(() => ({
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
        require('../static/streetactivity/js/colors.js');
        // pas pad aan
    });

    test('getBootstrapColors returns correct values', () => {
        const colors = window.MyColors.getBootstrapColors();
        expect(colors.primary).toBe('rgba(1,2,3,0.95)');
        expect(colors.danger).toBe('rgba(4,5,6,0.9)');
    });

    test('mapConfidenceLevelToColor works', () => {
        const colors = {
            danger: 'red',
            warning: 'yellow',
            success: 'green',
            secondary: 'grey',
        };
        expect(window.MyColors.mapConfidenceLevelToColor(0, colors)).toBe('red');
        expect(window.MyColors.mapConfidenceLevelToColor(42, colors)).toBe('grey');
    });

    test('mapConfidenceLevelsToColors works', () => {
        const colors = {
            danger: 'red',
            warning: 'yellow',
            success: 'green',
            secondary: 'grey',
        };
        expect(window.MyColors.mapConfidenceLevelsToColors([0,1,2], colors)).toEqual(['red','yellow','green']);
    });
});
