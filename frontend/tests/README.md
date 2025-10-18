# FLUX Frontend Testing

This directory contains comprehensive tests for the FLUX frontend application.

## Test Setup

### Prerequisites

Install dependencies:
```bash
cd frontend
npm install
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (auto-rerun on file changes)
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run tests in CI mode (for continuous integration)
npm run test:ci
```

## Test Files

### LiveTheater.test.tsx

Comprehensive tests for the Live Research Theater page (`app/flow/[id]/page.tsx`).

**Test Coverage:**

1. **Initial Rendering**
   - Loading state on connection
   - Research question display
   - Header elements

2. **SSE Connection**
   - Connects with correct research ID
   - Shows LIVE indicator when connected
   - Handles query parameters

3. **Message Display**
   - Displays messages as they arrive from stream
   - Renders agent names and content
   - Shows message metadata

4. **Phase Progress**
   - Updates when phase changes
   - Displays correct iteration count (Orbit X/Y)
   - Shows progress percentage

5. **Active Agent Highlighting**
   - Highlights current active agent
   - Dims inactive agents
   - Updates on agent changes

6. **Quality Scores**
   - Displays scores from Filter agent
   - Shows quality history
   - Updates in real-time

7. **Connection Error Handling**
   - Handles reconnection attempts
   - Shows reconnecting state
   - Displays error messages
   - Provides retry functionality
   - Fails gracefully after max attempts

8. **Completion**
   - Shows COMPLETE indicator
   - Displays celebration animation
   - Provides View Paper button
   - Navigates to paper detail page

9. **Cleanup**
   - Closes EventSource on unmount
   - Clears timeouts and intervals
   - Prevents memory leaks

10. **Accessibility**
    - Proper ARIA labels
    - Keyboard navigation support
    - Focus management
    - Screen reader compatibility

11. **Mobile Responsiveness**
    - Adapts layout for mobile (< 768px)
    - Adapts layout for tablet (768px - 1024px)
    - Shows/hides mobile stats toggle
    - Horizontal agent scroll on mobile

12. **Integration**
    - Full lifecycle from connect to complete
    - State transitions
    - Component interactions

## Testing Patterns

### Mocking

The tests mock several key dependencies:

- **Next.js Navigation**: `useRouter`, `useParams`, `useSearchParams`
- **useResearchStream Hook**: Custom hook for SSE connection
- **Child Components**: AgentAvatar, ConversationFeed, PhaseProgress, LiveStats, ConnectionStatus
- **Browser APIs**: EventSource, IntersectionObserver, ResizeObserver, matchMedia

### Test Structure

```typescript
describe("Component/Feature", () => {
  beforeEach(() => {
    // Setup mocks and clear state
  });

  it("should do something specific", () => {
    // Arrange: Set up test data
    // Act: Trigger the behavior
    // Assert: Verify the result
  });
});
```

### Async Testing

For SSE and async operations:

```typescript
await waitFor(() => {
  expect(screen.getByText(/expected text/i)).toBeInTheDocument();
});
```

### Accessibility Testing

```typescript
// Check for proper ARIA roles
const header = screen.getByRole("banner");
expect(header).toBeInTheDocument();

// Test keyboard navigation
const button = screen.getByRole("button", { name: /retry/i });
button.focus();
expect(button).toHaveFocus();
```

## Coverage Goals

Target coverage thresholds:
- Branches: 70%
- Functions: 70%
- Lines: 70%
- Statements: 70%

View coverage report:
```bash
npm run test:coverage
```

The coverage report will be generated in `coverage/lcov-report/index.html`.

## Continuous Integration

For CI environments, use:
```bash
npm run test:ci
```

This runs tests with:
- Coverage reporting
- Limited workers for resource efficiency
- CI-optimized output format
- Fail-fast on errors

## Writing New Tests

When adding new tests:

1. **Follow the AAA pattern**: Arrange, Act, Assert
2. **Test user behavior**, not implementation details
3. **Use semantic queries**: `getByRole`, `getByLabelText`, `getByText`
4. **Mock external dependencies** at the boundary
5. **Keep tests isolated** and independent
6. **Test accessibility** alongside functionality
7. **Use meaningful test descriptions** that explain the "why"

### Example

```typescript
it("displays error state when connection fails permanently", () => {
  // Arrange
  const mockReconnect = jest.fn();
  mockUseResearchStream.mockReturnValue({
    connectionStatus: ConnectionStatus.ERROR,
    error: "Connection failed after 10 attempts",
    reconnect: mockReconnect,
    // ... other state
  });

  // Act
  render(<FlowPage />);
  const retryButton = screen.getByRole("button", { name: /retry/i });
  fireEvent.click(retryButton);

  // Assert
  expect(screen.getByText(/connection failed after 10 attempts/i)).toBeInTheDocument();
  expect(mockReconnect).toHaveBeenCalled();
});
```

## Troubleshooting

### Common Issues

**Issue**: Tests timeout
- **Solution**: Increase Jest timeout in `jest.config.js` or use `jest.setTimeout(10000)` in tests

**Issue**: EventSource not defined
- **Solution**: Check `jest.setup.js` has EventSource mock

**Issue**: CSS/Tailwind classes not working
- **Solution**: Tests don't render CSS. Test behavior, not styling.

**Issue**: Component not found
- **Solution**: Ensure component is properly mocked in test file

### Debug Tests

Add `debug()` from React Testing Library:

```typescript
import { render, screen, debug } from "@testing-library/react";

it("debugging test", () => {
  render(<FlowPage />);
  screen.debug(); // Prints entire DOM
  screen.debug(screen.getByRole("button")); // Prints specific element
});
```

## Resources

- [React Testing Library Docs](https://testing-library.com/react)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Next.js Testing Guide](https://nextjs.org/docs/testing)

