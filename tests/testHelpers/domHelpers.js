/**
 * Helper om een mock input element te maken
 */
export const createMockInputElement = (options = {}) => {
  const element = {
    id: options.id || 'mock-input',
    value: options.value || '',
    parentNode: {
      appendChild: jest.fn()
    },
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn(),
    ...options
  };
  
  // Voeg classList toe als object properties
  if (!element.classList) {
    element.classList = {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    };
  }
  
  return element;
};

/**
 * Helper om een mock radio button element te maken
 */
export const createMockRadioElement = (options = {}) => {
  const mockCard = {
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    }
  };
  
  const mockRow = {
    querySelectorAll: jest.fn(() => [mockCard])
  };
  
  const element = {
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    checked: options.checked || false,
    ...options
  };
  
  // Mock closest functie
  element.closest = jest.fn((selector) => {
    if (selector === '.card') return mockCard;
    if (selector === '.row') return mockRow;
    return null;
  });
  
  // Sla mock data op voor assertions
  element._mockCard = mockCard;
  element._mockRow = mockRow;
  
  return element;
};

/**
 * Helper om een mock div element te maken
 */
export const createMockDivElement = (options = {}) => {
  const element = {
    className: options.className || '',
    textContent: options.textContent || '',
    style: options.style || {},
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    ...options
  };
  
  // Voeg classList toe
  if (!element.classList) {
    element.classList = {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn()
    };
  }
  
  return element;
};

/**
 * Setup document mocks
 */
export const setupDocumentMocks = () => {
  const originalDocument = global.document;
  const mocks = {
    document: {
      addEventListener: jest.fn(),
      getElementById: jest.fn(),
      querySelectorAll: jest.fn(),
      createElement: jest.fn(),
      querySelector: jest.fn()
    }
  };
  
  // Overschrijf document methods
  Object.keys(mocks.document).forEach(key => {
    global.document[key] = mocks.document[key];
  });
  
  return {
    mocks,
    restore: () => {
      if (originalDocument) {
        Object.keys(mocks.document).forEach(key => {
          global.document[key] = originalDocument[key];
        });
      }
    }
  };
};