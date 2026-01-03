describe('Tooltip functionality', () => {
  test('should return report snippet in tooltip', () => {
    const reportSnippets = ['First moment', 'Second moment', ''];
    
    // Simuleer de tooltip callback uit de chart configuratie
    const tooltipCallback = {
      label: function (context) {
        const index = context.dataIndex;
        return reportSnippets[index] || '';
      }
    };

    // Test met verschillende data indices
    expect(tooltipCallback.label({ dataIndex: 0 })).toBe('First moment');
    expect(tooltipCallback.label({ dataIndex: 1 })).toBe('Second moment');
    expect(tooltipCallback.label({ dataIndex: 2 })).toBe('');
    expect(tooltipCallback.label({ dataIndex: 99 })).toBe('');
  });

  test('should handle empty report snippets gracefully', () => {
    const reportSnippets = [null, undefined, ''];
    
    const tooltipCallback = {
      label: function (context) {
        const index = context.dataIndex;
        return reportSnippets[index] || '';
      }
    };

    expect(tooltipCallback.label({ dataIndex: 0 })).toBe('');
    expect(tooltipCallback.label({ dataIndex: 1 })).toBe('');
    expect(tooltipCallback.label({ dataIndex: 2 })).toBe('');
  });
});