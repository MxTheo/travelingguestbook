//This setup is run before each test file
//It is GLOBAL for all tests in all apps

// Mock de globale browser APIs
global.Chart = jest.fn(() => ({
  destroy: jest.fn(),
  update: jest.fn(),
  reset: jest.fn(),
}));

// Mock voor getComputedStyle
global.getComputedStyle = jest.fn(() => ({
  getPropertyValue: jest.fn(),
}));

// Mock voor matchMedia (nodig voor responsive design libraries)
global.matchMedia = jest.fn(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: jest.fn(),
  removeListener: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
}));

// Mock voor IntersectionObserver (nodig voor lazy loading)
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock voor ResizeObserver
global.ResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock voor localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock voor sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Console mocks (om test output schoon te houden)
global.console = {
  ...console,
  // Je kunt specifieke console methods uitzetten tijdens tests
  // log: jest.fn(),
  // error: jest.fn(),
  // warn: jest.fn(),
};

// DOM utility helpers voor tests
global.createMockElement = (attributes = {}) => {
  const element = {
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    removeAttribute: jest.fn(),
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      toggle: jest.fn(),
      contains: jest.fn(),
    },
    style: {},
    innerHTML: '',
    textContent: '',
    value: '',
    checked: false,
    focus: jest.fn(),
    blur: jest.fn(),
    click: jest.fn(),
    ...attributes,
  };
  
  return element;
};