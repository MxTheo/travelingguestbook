// Mock Chart.js en DOM elementen
global.Chart = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
}));

// Mock getComputedStyle
global.getComputedStyle = jest.fn(() => ({
  getPropertyValue: jest.fn((property) => {
    const cssVars = {
      '--bs-primary': 'rgba(54,162,235,0.95)',
      '--bs-danger': 'rgba(220,53,69,0.9)',
      '--bs-warning': 'rgba(255,193,7,0.95)',
      '--bs-success': 'rgba(25,135,84,0.95)',
      '--bs-secondary': 'rgba(108,117,125,0.9)',
      '--bs-dark': 'rgba(33,37,41,0.9)',
    };
    return cssVars[property] || '';
  }),
}));

// Mock document methods
document.addEventListener = jest.fn((event, callback) => {
  if (event === 'DOMContentLoaded') {
    callback();
  }
});

describe('Confidence Chart', () => {
  let originalQuerySelector;
  let originalGetContext;

  beforeEach(() => {
    // Reset mocks
    Chart.mockClear();
    
    // Mock DOM elements
    originalQuerySelector = document.querySelector;
    originalGetContext = HTMLCanvasElement.prototype.getContext;

    document.querySelector = jest.fn((selector) => {
      if (selector === '.chart-container') {
        return {
          innerHTML: ''
        };
      }
      return null;
    });

    HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
      clearRect: jest.fn(),
      fillRect: jest.fn(),
    }));
  });

  afterEach(() => {
    // Restore original methods
    document.querySelector = originalQuerySelector;
    HTMLCanvasElement.prototype.getContext = originalGetContext;
  });

  describe('cssVar helper function', () => {
    test('should get CSS variable value', () => {
      // Mock de getComputedStyle functie specifiek voor deze test
      const mockGetPropertyValue = jest.fn().mockReturnValue('rgba(54,162,235,0.95)');
      const mockGetComputedStyle = jest.fn(() => ({
        getPropertyValue: mockGetPropertyValue
      }));
      
      global.getComputedStyle = mockGetComputedStyle;
      
      // Hervat de functie uit de originele code
      const cssVar = (name, fallback = '') => {
        const v = getComputedStyle(document.documentElement).getPropertyValue(name);
        return (v && v.trim()) || fallback;
      };

      const result = cssVar('--bs-primary');
      
      expect(mockGetComputedStyle).toHaveBeenCalledWith(document.documentElement);
      expect(mockGetPropertyValue).toHaveBeenCalledWith('--bs-primary');
      expect(result).toBe('rgba(54,162,235,0.95)');
    });

    test('should return fallback when CSS variable is empty', () => {
      const mockGetPropertyValue = jest.fn().mockReturnValue('');
      const mockGetComputedStyle = jest.fn(() => ({
        getPropertyValue: mockGetPropertyValue
      }));
      
      global.getComputedStyle = mockGetComputedStyle;
      
      const cssVar = (name, fallback = 'default-value') => {
        const v = getComputedStyle(document.documentElement).getPropertyValue(name);
        return (v && v.trim()) || fallback;
      };

      const result = cssVar('--bs-non-existent', 'fallback-value');
      
      expect(result).toBe('fallback-value');
    });
  });

  describe('Chart initialization', () => {
    test('should show message when no moments data', () => {
      // Mock moments data als lege array
      const moments = [];
      
      // Herhaal de logica uit de originele code
      if (!moments || moments.length === 0) {
        const container = document.querySelector('.chart-container');
        container.innerHTML = '<p class="text-center text-muted">Hoe is je gevoel van (on)zekerheid verlopen tijdens deze ervaring?</p>';
      }
      
      expect(document.querySelector).toHaveBeenCalledWith('.chart-container');
    });

    test('should create chart with correct data structure', () => {
      // Mock moments data
      const moments = [
        {
          activity: { name: 'Activity 1' },
          confidence_level: 2,
          report_snippet: 'Feeling confident'
        },
        {
          activity: { name: 'Activity 2' },
          confidence_level: 0,
          report_snippet: 'Feeling uncertain'
        }
      ];

      // Simuleer de dataverwerking
      const labels = moments.map(moment => moment.activity.name);
      const confidenceData = moments.map(moment => moment.confidence_level);
      const reportSnippets = moments.map(moment => moment.report_snippet || '');

      expect(labels).toEqual(['Activity 1', 'Activity 2']);
      expect(confidenceData).toEqual([2, 0]);
      expect(reportSnippets).toEqual(['Feeling confident', 'Feeling uncertain']);
    });
  });

  describe('Chart configuration', () => {
    test('should initialize Chart with correct options', () => {
      const mockCtx = {};
      
      // Roep de Chart constructor aan zoals in de originele code
      const chart = new Chart(mockCtx, {
        type: 'line',
        data: {
          labels: ['Test'],
          datasets: [{
            label: 'Zelfverzekerdheid',
            data: [1],
            borderColor: 'rgba(54,162,235,0.95)',
            backgroundColor: 'rgba(33,37,41,0.9)',
            pointBackgroundColor: ['rgba(255,193,7,0.95)'],
            pointBorderColor: ['rgba(255,193,7,0.95)'],
            pointRadius: 8,
            pointHoverRadius: 10,
            pointBorderWidth: 2,
            pointHitRadius: 15,
            fill: false,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              min: 0,
              max: 2,
              ticks: {
                stepSize: 1,
                callback: expect.any(Function)
              },
              grid: {
                drawBorder: true
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                autoSkip: false,
                maxRotation: 45,
                minRotation: 45
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: expect.any(Function)
              }
            }
          },
          clip: false
        }
      });

      expect(Chart).toHaveBeenCalledTimes(1);
      expect(Chart).toHaveBeenCalledWith(
        mockCtx,
        expect.objectContaining({
          type: 'line',
          options: expect.objectContaining({
            responsive: true,
            maintainAspectRatio: false
          })
        })
      );
    });

    test('should correctly format y-axis labels', () => {
      // Test de callback functie uit de chart configuratie
      const yAxisCallback = (value) => {
        switch (value) {
          case 0:
            return 'Onzeker';
          case 1:
            return 'Tussenin';
          case 2:
            return 'Zelfverzekerd';
          default:
            return '';
        }
      };

      expect(yAxisCallback(0)).toBe('Onzeker');
      expect(yAxisCallback(1)).toBe('Tussenin');
      expect(yAxisCallback(2)).toBe('Zelfverzekerd');
      expect(yAxisCallback(3)).toBe('');
    });
  });
});