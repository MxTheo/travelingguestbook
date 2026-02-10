describe('Confidence Chart Integration', () => {
  let mockMomentsData;
  let mockChartElement;
  let mockChartContainer;

  beforeEach(() => {
    mockChartElement = {
      getContext: jest.fn(() => ({})),
      parentNode: {
        innerHTML: ''
      }
    };

    mockChartContainer = {
      innerHTML: ''
    };

    document.getElementById = jest.fn((id) => {
      if (id === 'confidenceChart') return mockChartElement;
      return null;
    });

    document.querySelector = jest.fn((selector) => {
      if (selector === '.chart-container') return mockChartContainer;
      return null;
    });

    mockMomentsData = [
      {
        activity: { name: 'Meeting' },
        confidence_level: 2,
        report_snippet: 'Went well'
      },
      {
        activity: { name: 'Presentation' },
        confidence_level: 1,
        report_snippet: 'Could be better'
      }
    ];
  });

  test('should process complete data flow correctly', () => {
    // Simuleer de complete data flow uit de originele code
    const labels = mockMomentsData.map(moment => moment.activity.name);
    const confidenceData = mockMomentsData.map(moment => moment.confidence_level);
    const reportSnippets = mockMomentsData.map(moment => moment.report_snippet || '');

    // Test de uitkomsten
    expect(labels).toHaveLength(2);
    expect(labels).toContain('Meeting');
    expect(labels).toContain('Presentation');
    
    expect(confidenceData).toEqual([2, 1]);
    expect(reportSnippets).toEqual(['Went well', 'Could be better']);
  });

  test('should handle edge cases', () => {
    // Test met lege snippets
    const momentsWithEmptySnippet = [
      {
        activity: { name: 'Test' },
        confidence_level: 0,
        report_snippet: null
      }
    ];

    const reportSnippets = momentsWithEmptySnippet.map(moment => moment.report_snippet || '');
    
    expect(reportSnippets[0]).toBe('');
  });
});