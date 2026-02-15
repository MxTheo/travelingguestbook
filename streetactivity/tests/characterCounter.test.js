describe('Character Counter', () => {
  test('should calculate remaining characters correctly', () => {
    const maxLength = 367;
    
    const calculateDisplay = (text) => {
      const remaining = maxLength - text.length;
      return {
        text: `${text.length}/${maxLength} karakters`,
        className: `form-text text-end ${remaining < 50 ? 'text-warning' : 'text-muted'}`
      };
    };
    
    expect(calculateDisplay('')).toEqual({
      text: '0/367 karakters',
      className: 'form-text text-end text-muted'
    });
    
    expect(calculateDisplay('Hello')).toEqual({
      text: '5/367 karakters',
      className: 'form-text text-end text-muted'
    });
    
    expect(calculateDisplay('a'.repeat(317))).toEqual({
      text: '317/367 karakters',
      className: 'form-text text-end text-muted'
    });
  });
  
  test('should handle edge cases', () => {
    const maxLength = 367;
    
    const shouldShowWarning = (text) => {
      const remaining = maxLength - text.length;
      return remaining < 50;
    };
    
    expect(shouldShowWarning('')).toBe(false);
    expect(shouldShowWarning('a'.repeat(317))).toBe(false); // 50 remaining
    expect(shouldShowWarning('a'.repeat(318))).toBe(true); // 49 remaining
    expect(shouldShowWarning('a'.repeat(367))).toBe(true); // 0 remaining
  });
});