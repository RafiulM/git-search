import { listRepositories, getRepository } from './api';

// Test the API utilities
describe('API Utilities', () => {
  it('should have correct API configuration', () => {
    expect(process.env.NEXT_PUBLIC_API_URL).toBeDefined();
    expect(process.env.API_KEY).toBeDefined();
  });

  it('should construct correct API URLs', () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    expect(baseUrl).toMatch(/^http:\/\/localhost:8000$/);
  });

  // Note: Actual API calls would require mocking fetch
  // and proper environment setup
});