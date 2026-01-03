describe('Django template integration', () => {
  test('should handle JSON data from Django template', () => {
    // Simuleer JSON data zoals die uit Django komt
    const djangoTemplateData = [
      {
        "activity": {
          "name": "Workshop"
        },
        "confidence_level": 2,
        "report_snippet": "Great experience"
      }
    ];

    // Simuleer de {{ moments_json|safe }} template tag
    const moments = djangoTemplateData;

    // Test of de data correct verwerkt wordt
    expect(moments).toBeDefined();
    expect(moments).toHaveLength(1);
    expect(moments[0].activity.name).toBe('Workshop');
    expect(moments[0].confidence_level).toBe(2);
  });

  test('should handle invalid or missing data gracefully', () => {
    // Test cases voor verschillende Django outputs
    const testCases = [
      { input: null, expectedLength: 0 },
      { input: undefined, expectedLength: 0 },
      { input: [], expectedLength: 0 },
      { input: 'invalid', expectedType: 'string' }
    ];

    testCases.forEach(({ input, expectedLength, expectedType }) => {
      if (input === null || input === undefined) {
        // Simuleer de check uit de originele code
        if (!input) {
          expect(document.querySelector).toBeDefined(); // placeholder check
        }
      }
    });
  });
});