module.exports = {
  // Test environment voor DOM manipulatie
  testEnvironment: 'jsdom',
  
  // Waar zijn je testbestanden?
  testMatch: [
    '**/tests/**/*.test.js',
    '**/__tests__/**/*.test.js',
  ],
  
  // Welke mappen negeren?
  testPathIgnorePatterns: [
    '/node_modules/',
    '/.venv/',
    '/venv/',
    '/static/',
    '/media/',
    '/migrations/',
    '/__pycache__/',
    '/coverage/',
    '/tests/testHelpers/', 
  ],
  
  collectCoverageFrom: [
    '**/static/js/**/*.js',
    '!**/node_modules/**',
    '!**/.venv/**',
    '!**/venv/**',
    '!**/env/**',
    '!**/migrations/**',
    '!**/__pycache__/**',
    '!**/*.django.js', 
    '!**/*.tpl.js',
  ],

  collectCoverage: true,

  // Ignore transform for specific files
  transformIgnorePatterns: [
    '/node_modules/',
    '\\.django\\.js$',
    '\\.tpl\\.js$',
  ],

  // Setup file die voor elke test wordt gerund
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
  // Module mapping (handig als je CSS/SCSS imports hebt)
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': 
      '<rootDir>/tests/__mocks__/fileMock.js',
  },
  
  
  // Coverage directory
  coverageDirectory: '<rootDir>/tests/coverage',
  
  // Coverage reporters
  coverageReporters: ['json', 'lcov', 'text', 'clover', 'html'],
};