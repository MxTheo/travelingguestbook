module.exports = {
  // Test environment voor DOM manipulatie
  testEnvironment: 'jsdom',
  
  // Waar zijn je testbestanden?
  testMatch: [
    '<rootDir>/**/tests/**/*.test.js',
    '<rootDir>/**/tests/**/*.spec.js',
    '<rootDir>/**/__tests__/**/*.test.js',
    '<rootDir>/**/__tests__/**/*.spec.js',
  ],
  
  // Welke mappen negeren?
  testPathIgnorePatterns: [
    '/node_modules/',
    '/venv/',
    '/.env/',
    '/static/',
    '/media/',
    '/migrations/',
  ],
  
  // Setup file die voor elke test wordt gerund
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  
  // Module mapping (handig als je CSS/SCSS imports hebt)
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': 
      '<rootDir>/tests/__mocks__/fileMock.js',
  },
  
  // Coverage reporting
  collectCoverage: true,
  collectCoverageFrom: [
    '**/static/js/**/*.js',
    '**/templates/**/*.js',
    '!**/node_modules/**',
    '!**/vendor/**',
    '!**/dist/**',
    '!**/build/**',
  ],
  
  // Coverage directory
  coverageDirectory: '<rootDir>/tests/coverage',
  
  // Coverage reporters
  coverageReporters: ['json', 'lcov', 'text', 'clover', 'html'],
};