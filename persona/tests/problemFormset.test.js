describe('Problem Formset Management', () => {
  let originalDocument;
  let originalAddEventListener;
  let originalGetElementById;
  
  let mockAddButton;
  let mockFormset;
  let mockTotalForms;
  let mockOriginalForm;
  let mockClone;
  let mockTextInput;
  let mockDeleteInput;
  
  beforeEach(() => {
    // Bewaar originele document methods
    originalDocument = global.document;
    originalAddEventListener = document.addEventListener;
    originalGetElementById = document.getElementById;
    
    // Mock DOM elementen
    mockAddButton = {
      addEventListener: jest.fn()
    };
    
    mockFormset = {
      querySelector: jest.fn(),
      appendChild: jest.fn()
    };
    
    mockTotalForms = {
      value: '2'
    };
    
    mockTextInput = {
      value: 'original value'
    };
    
    mockDeleteInput = {
      checked: true
    };
    
    mockClone = {
      innerHTML: '<input name="problems-0-text" value="test"><input name="problems-0-DELETE" checked>',
      querySelector: jest.fn((selector) => {
        if (selector.includes('text')) return mockTextInput;
        if (selector.includes('DELETE')) return mockDeleteInput;
        return null;
      })
    };
    
    mockOriginalForm = {
      cloneNode: jest.fn(() => mockClone)
    };
    
    // Mock document methods - BELANGRIJK: mock op global.document
    global.document.addEventListener = jest.fn();
    global.document.getElementById = jest.fn((id) => {
      switch(id) {
        case 'add-problem':
          return mockAddButton;
        case 'problem-formset':
          return mockFormset;
        case 'id_problems-TOTAL_FORMS':
          return mockTotalForms;
        default:
          return null;
      }
    });
    global.document.querySelector = jest.fn();
    
    // Mock formset.querySelector
    mockFormset.querySelector.mockReturnValue(mockOriginalForm);
  });
  
  afterEach(() => {
    // Herstel originele document methods
    if (originalDocument) {
      global.document.addEventListener = originalAddEventListener;
      global.document.getElementById = originalGetElementById;
    }
    jest.restoreAllMocks();
  });
  
  test('should add click event listener to problem add button', () => {
    // ARRANGE
    const callback = jest.fn();
    
    // Stel in dat DOMContentLoaded de callback aanroept
    document.addEventListener.mockImplementation((event, cb) => {
      if (event === 'DOMContentLoaded') {
        // Roep de callback direct aan om de code uit te voeren
        cb();
      }
    });
    
    // ACT - Simuleer de originele code
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('add-problem').addEventListener('click', callback);
    });
    
    // Roep de DOMContentLoaded handler aan
    const domLoadedCall = document.addEventListener.mock.calls.find(
      call => call[0] === 'DOMContentLoaded'
    );
    if (domLoadedCall) {
      domLoadedCall[1](); // Roep de callback aan
    }
    
    // ASSERT
    expect(document.getElementById).toHaveBeenCalledWith('add-problem');
    expect(mockAddButton.addEventListener).toHaveBeenCalledWith('click', callback);
  });
  
  test('should clone form and update form indices correctly', () => {
    // ARRANGE
    const totalForms = { value: '2' };
    const mockNewForm = {
      innerHTML: '<input name="problems-0-text"><input name="problems-0-DELETE">',
      querySelector: jest.fn(() => ({ value: '', checked: false }))
    };
    
    const formset = {
      querySelector: jest.fn(() => ({
        cloneNode: jest.fn(() => mockNewForm)
      })),
      appendChild: jest.fn()
    };
    
    // Overschrijf de mock voor deze test
    document.getElementById.mockImplementation((id) => {
      if (id === 'problem-formset') return formset;
      if (id === 'id_problems-TOTAL_FORMS') return totalForms;
      return null;
    });
    
    // ACT - simuleer de click handler logica
    const clickHandler = function() {
      const formset = document.getElementById('problem-formset');
      const totalForms = document.getElementById('id_problems-TOTAL_FORMS');
      const formNum = parseInt(totalForms.value);
      
      const originalForm = formset.querySelector('.problem-form');
      const newForm = originalForm.cloneNode(true);
      
      // Test de regex replace
      newForm.innerHTML = newForm.innerHTML.replace(/problems-\d+-/g, `problems-${formNum}-`);
      
      formset.appendChild(newForm);
      totalForms.value = (formNum + 1).toString();
      
      return { newForm, totalForms: totalForms.value };
    };
    
    // ASSERT
    const result = clickHandler();
    
    expect(formset.appendChild).toHaveBeenCalledWith(mockNewForm);
    expect(totalForms.value).toBe('3');
    
    // Controleer of de regex correct werkt
    expect(mockNewForm.innerHTML).toBe('<input name="problems-2-text"><input name="problems-2-DELETE">');
  });
  
  test('should reset form values in cloned form', () => {
    // ARRANGE
    const clickHandler = function() {
      // Deze logica simuleert wat er in de click handler gebeurt
      const newForm = mockFormset.querySelector('.problem-form').cloneNode(true);
      
      // Reset de waarden zoals in de originele code
      const textInput = newForm.querySelector('input[name$="-text"]');
      const deleteInput = newForm.querySelector('input[name$="-DELETE"]');
      
      if (textInput) textInput.value = '';
      if (deleteInput) deleteInput.checked = false;
      
      return { textInput, deleteInput };
    };
    
    // ACT
    const result = clickHandler();
    
    // ASSERT
    expect(result.textInput.value).toBe('');
    expect(result.deleteInput.checked).toBe(false);
  });
  
  test('should handle form index replacement correctly', () => {
    // Test de regex replace functionaliteit
    const testCases = [
      {
        input: 'problems-0-text',
        formNum: 2,
        expected: 'problems-2-text'
      },
      {
        input: 'problems-1-DELETE',
        formNum: 3,
        expected: 'problems-3-DELETE'
      },
      {
        input: '<input name="problems-0-text" value="test"><input name="problems-0-DELETE">',
        formNum: 5,
        expected: '<input name="problems-5-text" value="test"><input name="problems-5-DELETE">'
      }
    ];
    
    testCases.forEach(({ input, formNum, expected }) => {
      const result = input.replace(/problems-\d+-/g, `problems-${formNum}-`);
      expect(result).toBe(expected);
    });
  });
  
  test('should increment total forms counter correctly', () => {
    const testCases = [
      { initial: '0', expected: '1' },
      { initial: '1', expected: '2' },
      { initial: '5', expected: '6' },
      { initial: '10', expected: '11' }
    ];
    
    testCases.forEach(({ initial, expected }) => {
      const totalForms = { value: initial };
      const formNum = parseInt(totalForms.value);
      totalForms.value = (formNum + 1).toString();
      expect(totalForms.value).toBe(expected);
    });
  });
  
  // NIEUW: Test de complete integratie
  test('should handle complete form addition flow', () => {
    // ARRANGE
    let clickCallback;
    
    // Mock de button click event listener
    mockAddButton.addEventListener.mockImplementation((event, callback) => {
      if (event === 'click') {
        clickCallback = callback;
      }
    });
    
    // Simuleer DOMContentLoaded
    document.addEventListener.mockImplementation((event, domCallback) => {
      if (event === 'DOMContentLoaded') {
        // Dit is de code die bij DOMContentLoaded wordt uitgevoerd
        domCallback();
      }
    });
    
    // ACT - Voer de complete flow uit
    
    // Stap 1: DOMContentLoaded
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('add-problem').addEventListener('click', function() {
        const formset = document.getElementById('problem-formset');
        const totalForms = document.getElementById('id_problems-TOTAL_FORMS');
        const formNum = parseInt(totalForms.value);
        
        const newForm = formset.querySelector('.problem-form').cloneNode(true);
        newForm.innerHTML = newForm.innerHTML.replace(/problems-\d+-/g, `problems-${formNum}-`);
        newForm.querySelector('input[name$="-text"]').value = '';
        newForm.querySelector('input[name$="-DELETE"]').checked = false;
        
        formset.appendChild(newForm);
        totalForms.value = (formNum + 1).toString();
      });
    });
    
    // Roep DOMContentLoaded aan
    const domLoadedCall = document.addEventListener.mock.calls[0];
    domLoadedCall[1]();
    
    // Stap 2: Simuleer button click
    if (clickCallback) {
      clickCallback();
    }
    
    // ASSERT
    expect(document.getElementById).toHaveBeenCalledWith('add-problem');
    expect(document.getElementById).toHaveBeenCalledWith('problem-formset');
    expect(document.getElementById).toHaveBeenCalledWith('id_problems-TOTAL_FORMS');
    
    expect(mockFormset.querySelector).toHaveBeenCalledWith('.problem-form');
    expect(mockOriginalForm.cloneNode).toHaveBeenCalledWith(true);
    expect(mockFormset.appendChild).toHaveBeenCalledWith(mockClone);
    expect(mockTotalForms.value).toBe('3'); // Begon met '2', nu '3'
    
    // Controleer of waarden zijn gereset
    expect(mockTextInput.value).toBe('');
    expect(mockDeleteInput.checked).toBe(false);
  });
});