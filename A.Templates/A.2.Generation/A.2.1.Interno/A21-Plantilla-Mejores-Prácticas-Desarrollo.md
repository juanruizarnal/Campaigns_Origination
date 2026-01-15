# Rule: Generating a Development Best Practices and Standards Guide

## Goal

To guide a CTO Agent in creating a comprehensive Development Best Practices and Standards Guide in Markdown format, based on an existing Product Requirements Document (PRD), technology stack analysis, and additional project context. The guide should establish clear coding standards, architectural principles, development methodologies, and specific rules that all developers must follow to ensure code quality, maintainability, security, and team collaboration throughout the project lifecycle.

## Process

1. **Receive Context:** The CTO Agent receives the PRD, technology stack analysis, and additional project context (team size, experience levels, project timeline, quality requirements).
2. **Analyze Requirements:** Extract development requirements, quality standards, and team collaboration needs.
3. **Define Standards:** Establish comprehensive coding standards, architectural principles, and development workflows.
4. **Create Guidelines:** Develop specific, actionable guidelines for each aspect of development.
5. **Establish Enforcement:** Define code review processes, automated checks, and quality gates.
6. **Generate Guide:** Create comprehensive guide using the structure outlined below.
7. **Save Guide:** Save the document as `development-best-practices-[project-name].md` in the `/03-Tasks/` directory.

## Standards Framework

The CTO Agent must establish standards across these critical areas:

### Code Quality Standards
- **Readability:** Naming conventions, code structure, documentation requirements
- **Maintainability:** Modularity, separation of concerns, refactoring guidelines
- **Performance:** Optimization principles, resource management, caching strategies
- **Security:** Secure coding practices, vulnerability prevention, data protection
- **Testing:** Unit testing, integration testing, test coverage requirements

### Architectural Standards
- **Design Patterns:** Approved patterns, anti-patterns to avoid, implementation guidelines
- **Code Organization:** Project structure, module organization, dependency management
- **API Design:** RESTful principles, GraphQL standards, versioning strategies
- **Database Design:** Schema design, query optimization, migration strategies
- **Integration:** Service communication, error handling, monitoring requirements

### Development Workflow Standards
- **Version Control:** Git workflows, branching strategies, commit conventions
- **Code Review:** Review process, criteria, approval requirements
- **CI/CD:** Build processes, testing automation, deployment procedures
- **Documentation:** Code documentation, API documentation, architectural documentation
- **Quality Assurance:** Static analysis, automated testing, performance monitoring

## Guide Structure

The generated Development Best Practices and Standards Guide must include the following sections:

### 1. Executive Summary
- **Purpose:** Clear statement of the guide's objectives and scope
- **Compliance Requirements:** Mandatory vs. recommended practices
- **Quality Goals:** Measurable quality objectives and success criteria
- **Enforcement Strategy:** How standards will be monitored and enforced
- **Update Process:** How and when standards will be reviewed and updated

### 2. Project Context & Technology Stack
- **Project Overview:** Brief summary of project goals and requirements from PRD
- **Technology Stack:** Selected technologies and their implications for development practices
- **Team Structure:** Development team composition, roles, and responsibilities
- **Quality Requirements:** Specific quality, performance, and security requirements
- **Constraints:** Timeline, budget, regulatory, and technical constraints

### 3. Coding Standards

#### 3.1 General Principles
- **Clean Code Philosophy:** Fundamental principles for writing maintainable code
- **SOLID Principles:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY Principle:** Don't Repeat Yourself - code reusability guidelines
- **KISS Principle:** Keep It Simple, Stupid - simplicity over complexity
- **YAGNI Principle:** You Aren't Gonna Need It - avoiding over-engineering

#### 3.2 Language-Specific Standards

##### [PRIMARY_LANGUAGE] Standards
**Naming Conventions:**
- **Variables:** [Specific naming rules with examples]
  ```[language]
  // Good
  const userAccountBalance = 1500.00;
  const isEmailVerified = true;
  
  // Bad
  const uab = 1500.00;
  const flag = true;
  ```

- **Functions/Methods:** [Specific naming rules with examples]
  ```[language]
  // Good
  function calculateMonthlyInterest(principal, rate) { }
  async function fetchUserProfile(userId) { }
  
  // Bad
  function calc(p, r) { }
  function getData(id) { }
  ```

- **Classes:** [Specific naming rules with examples]
- **Constants:** [Specific naming rules with examples]
- **Files/Modules:** [Specific naming rules with examples]

**Code Structure:**
- **Function Length:** Maximum lines per function (recommended: 20-30 lines)
- **Class Length:** Maximum lines per class (recommended: 200-300 lines)
- **Parameter Count:** Maximum parameters per function (recommended: 3-5)
- **Nesting Depth:** Maximum nesting levels (recommended: 3-4 levels)
- **Cyclomatic Complexity:** Maximum complexity score (recommended: 10)

**Documentation Requirements:**
```[language]
/**
 * Calculates the compound interest for a given principal amount
 * @param {number} principal - The initial amount of money
 * @param {number} rate - The annual interest rate (as decimal)
 * @param {number} time - The time period in years
 * @param {number} frequency - Compounding frequency per year
 * @returns {number} The final amount after compound interest
 * @throws {Error} When any parameter is negative or invalid
 * @example
 * const finalAmount = calculateCompoundInterest(1000, 0.05, 2, 12);
 * console.log(finalAmount); // 1104.89
 */
function calculateCompoundInterest(principal, rate, time, frequency) {
  // Implementation
}
```

#### 3.3 Cross-Language Standards
- **Error Handling:** Consistent error handling patterns across all languages
- **Logging:** Standardized logging levels, formats, and practices
- **Configuration:** Environment-specific configuration management
- **Dependency Management:** Package/library selection and version management

### 4. Architectural Guidelines

#### 4.1 Design Patterns

##### Approved Patterns
**Creational Patterns:**
- **Factory Pattern:** [When to use, implementation example, benefits]
- **Singleton Pattern:** [When to use, implementation example, caveats]
- **Builder Pattern:** [When to use, implementation example, benefits]

**Structural Patterns:**
- **Adapter Pattern:** [When to use, implementation example, benefits]
- **Decorator Pattern:** [When to use, implementation example, benefits]
- **Facade Pattern:** [When to use, implementation example, benefits]

**Behavioral Patterns:**
- **Observer Pattern:** [When to use, implementation example, benefits]
- **Strategy Pattern:** [When to use, implementation example, benefits]
- **Command Pattern:** [When to use, implementation example, benefits]

##### Anti-Patterns to Avoid
- **God Object:** [Why to avoid, how to refactor, alternatives]
- **Spaghetti Code:** [Why to avoid, how to prevent, refactoring strategies]
- **Copy-Paste Programming:** [Why to avoid, how to prevent, alternatives]
- **Magic Numbers:** [Why to avoid, how to prevent, alternatives]

#### 4.2 Code Organization

##### Project Structure
```
project-root/
├── src/
│   ├── components/          # Reusable UI components
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions
│   ├── types/              # Type definitions
│   ├── constants/          # Application constants
│   └── config/             # Configuration files
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/
│   ├── api/                # API documentation
│   ├── architecture/       # Architecture documentation
│   └── deployment/         # Deployment guides
└── scripts/
    ├── build/              # Build scripts
    ├── deploy/             # Deployment scripts
    └── maintenance/        # Maintenance scripts
```

##### Module Organization
- **Single Responsibility:** Each module should have one clear purpose
- **High Cohesion:** Related functionality should be grouped together
- **Low Coupling:** Minimize dependencies between modules
- **Clear Interfaces:** Well-defined public APIs for each module
- **Dependency Direction:** Dependencies should flow in one direction

#### 4.3 API Design Standards

##### RESTful API Guidelines
**Resource Naming:**
```
GET    /api/v1/users              # Get all users
GET    /api/v1/users/{id}         # Get specific user
POST   /api/v1/users              # Create new user
PUT    /api/v1/users/{id}         # Update entire user
PATCH  /api/v1/users/{id}         # Partial user update
DELETE /api/v1/users/{id}         # Delete user
```

**HTTP Status Codes:**
- **200 OK:** Successful GET, PUT, PATCH
- **201 Created:** Successful POST
- **204 No Content:** Successful DELETE
- **400 Bad Request:** Invalid request data
- **401 Unauthorized:** Authentication required
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource not found
- **422 Unprocessable Entity:** Validation errors
- **500 Internal Server Error:** Server errors

**Response Format:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

**Error Response Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### 5. Security Standards

#### 5.1 Secure Coding Practices

##### Input Validation
- **Validate All Inputs:** Never trust user input or external data
- **Whitelist Approach:** Define what is allowed rather than what is forbidden
- **Sanitization:** Clean input data before processing
- **Length Limits:** Enforce maximum input lengths
- **Type Checking:** Validate data types and formats

```[language]
// Good - Input validation example
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email || typeof email !== 'string') {
    throw new Error('Email is required and must be a string');
  }
  
  if (email.length > 254) {
    throw new Error('Email is too long');
  }
  
  if (!emailRegex.test(email)) {
    throw new Error('Invalid email format');
  }
  
  return email.toLowerCase().trim();
}
```

##### Authentication & Authorization
- **Strong Password Policies:** Minimum length, complexity requirements
- **Multi-Factor Authentication:** Implement 2FA where possible
- **Session Management:** Secure session handling and timeout
- **Role-Based Access Control:** Implement proper authorization checks
- **JWT Best Practices:** Secure token generation and validation

##### Data Protection
- **Encryption at Rest:** Encrypt sensitive data in databases
- **Encryption in Transit:** Use HTTPS/TLS for all communications
- **Secrets Management:** Never hardcode secrets in source code
- **Data Minimization:** Collect and store only necessary data
- **Secure Deletion:** Properly delete sensitive data when no longer needed

#### 5.2 Vulnerability Prevention

##### Common Vulnerabilities
**SQL Injection Prevention:**
```[language]
// Bad - Vulnerable to SQL injection
const query = `SELECT * FROM users WHERE email = '${userEmail}'`;

// Good - Using parameterized queries
const query = 'SELECT * FROM users WHERE email = ?';
const result = await db.query(query, [userEmail]);
```

**XSS Prevention:**
```[language]
// Bad - Vulnerable to XSS
element.innerHTML = userInput;

// Good - Escaped output
element.textContent = userInput;
// Or using a sanitization library
element.innerHTML = DOMPurify.sanitize(userInput);
```

**CSRF Prevention:**
- Implement CSRF tokens for state-changing operations
- Use SameSite cookie attributes
- Validate referrer headers for sensitive operations

### 6. Testing Standards

#### 6.1 Testing Strategy

##### Test Pyramid
```
    /\
   /  \     E2E Tests (10%)
  /____\    
 /      \   Integration Tests (20%)
/__________\ Unit Tests (70%)
```

##### Testing Principles
- **Test-Driven Development (TDD):** Write tests before implementation when possible
- **Behavior-Driven Development (BDD):** Focus on business behavior and requirements
- **Test Coverage:** Maintain minimum 80% code coverage for critical paths
- **Test Independence:** Tests should not depend on each other
- **Fast Feedback:** Tests should run quickly and provide immediate feedback

#### 6.2 Unit Testing Standards

##### Test Structure (AAA Pattern)
```[language]
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user with valid data', async () => {
      // Arrange
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'SecurePass123!'
      };
      const mockRepository = {
        save: jest.fn().mockResolvedValue({ id: 1, ...userData })
      };
      const userService = new UserService(mockRepository);

      // Act
      const result = await userService.createUser(userData);

      // Assert
      expect(result).toEqual({
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
        password: 'SecurePass123!'
      });
      expect(mockRepository.save).toHaveBeenCalledWith(userData);
    });

    it('should throw error when email is invalid', async () => {
      // Arrange
      const userData = {
        name: 'John Doe',
        email: 'invalid-email',
        password: 'SecurePass123!'
      };
      const userService = new UserService();

      // Act & Assert
      await expect(userService.createUser(userData))
        .rejects
        .toThrow('Invalid email format');
    });
  });
});
```

##### Test Naming Conventions
- **Descriptive Names:** Test names should clearly describe what is being tested
- **Given-When-Then:** Structure test names to describe the scenario
- **Consistent Format:** Use consistent naming patterns across all tests

#### 6.3 Integration Testing Standards
- **Database Tests:** Test database interactions with real or test databases
- **API Tests:** Test API endpoints with actual HTTP requests
- **Service Integration:** Test interactions between different services
- **External Dependencies:** Test integrations with third-party services

#### 6.4 End-to-End Testing Standards
- **User Journeys:** Test complete user workflows
- **Cross-Browser Testing:** Ensure compatibility across different browsers
- **Performance Testing:** Test application performance under load
- **Accessibility Testing:** Ensure application meets accessibility standards

### 7. Version Control Standards

#### 7.1 Git Workflow

##### Branching Strategy (GitFlow)
```
main
├── develop
│   ├── feature/user-authentication
│   ├── feature/payment-integration
│   └── feature/dashboard-redesign
├── release/v1.2.0
└── hotfix/critical-security-patch
```

**Branch Types:**
- **main:** Production-ready code only
- **develop:** Integration branch for features
- **feature/*:** Individual feature development
- **release/*:** Release preparation and bug fixes
- **hotfix/*:** Critical production fixes

##### Commit Message Standards
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **style:** Code style changes (formatting, etc.)
- **refactor:** Code refactoring
- **test:** Adding or updating tests
- **chore:** Maintenance tasks

**Examples:**
```
feat(auth): add multi-factor authentication

Implement TOTP-based 2FA for enhanced security.
Users can now enable 2FA in their profile settings.

Closes #123
```

```
fix(api): resolve memory leak in user service

Fix memory leak caused by unclosed database connections
in the user service. Connections are now properly closed
in finally blocks.

Fixes #456
```

#### 7.2 Code Review Process

##### Review Checklist
**Functionality:**
- [ ] Code works as intended and meets requirements
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive
- [ ] Performance implications are considered

**Code Quality:**
- [ ] Code follows established coding standards
- [ ] Functions and classes have single responsibilities
- [ ] Code is readable and well-documented
- [ ] No code duplication or magic numbers

**Security:**
- [ ] Input validation is implemented
- [ ] No sensitive data is exposed
- [ ] Authentication and authorization are proper
- [ ] Security best practices are followed

**Testing:**
- [ ] Adequate test coverage is provided
- [ ] Tests are meaningful and well-structured
- [ ] All tests pass successfully
- [ ] Integration points are tested

##### Review Guidelines
- **Constructive Feedback:** Focus on code, not the person
- **Explain Reasoning:** Provide context for suggested changes
- **Suggest Alternatives:** Offer better solutions when possible
- **Acknowledge Good Work:** Recognize well-written code
- **Timely Reviews:** Complete reviews within 24 hours

### 8. Documentation Standards

#### 8.1 Code Documentation

##### Inline Comments
```[language]
// Good - Explains why, not what
// Using exponential backoff to handle rate limiting
const delay = Math.pow(2, retryCount) * 1000;

// Bad - Explains what the code does (obvious)
// Multiply 2 by retryCount and then by 1000
const delay = Math.pow(2, retryCount) * 1000;
```

##### Function Documentation
- **Purpose:** What the function does
- **Parameters:** Description of each parameter
- **Return Value:** What the function returns
- **Exceptions:** What errors might be thrown
- **Examples:** Usage examples when helpful

#### 8.2 API Documentation
- **OpenAPI/Swagger:** Use standardized API documentation
- **Request/Response Examples:** Provide realistic examples
- **Error Codes:** Document all possible error responses
- **Authentication:** Explain authentication requirements
- **Rate Limiting:** Document any rate limiting policies

#### 8.3 Architecture Documentation
- **System Overview:** High-level architecture diagrams
- **Component Interactions:** How different parts communicate
- **Data Flow:** How data moves through the system
- **Deployment Architecture:** Infrastructure and deployment setup
- **Decision Records:** Document important architectural decisions

### 9. Performance Standards

#### 9.1 Performance Guidelines

##### Response Time Targets
- **API Endpoints:** < 200ms for 95th percentile
- **Database Queries:** < 100ms for simple queries
- **Page Load Times:** < 2 seconds for initial load
- **Interactive Elements:** < 100ms response to user actions

##### Resource Usage
- **Memory Usage:** Monitor and optimize memory consumption
- **CPU Usage:** Avoid CPU-intensive operations in main thread
- **Network Usage:** Minimize unnecessary network requests
- **Storage Usage:** Optimize database queries and indexes

#### 9.2 Optimization Techniques

##### Database Optimization
- **Indexing Strategy:** Create appropriate indexes for query patterns
- **Query Optimization:** Use EXPLAIN to analyze query performance
- **Connection Pooling:** Reuse database connections efficiently
- **Caching Strategy:** Implement appropriate caching layers

##### Frontend Optimization
- **Code Splitting:** Load only necessary code for each page
- **Image Optimization:** Compress and serve appropriate image formats
- **Caching Strategy:** Implement browser and CDN caching
- **Bundle Size:** Monitor and minimize JavaScript bundle sizes

### 10. Monitoring and Logging Standards

#### 10.1 Logging Standards

##### Log Levels
- **ERROR:** System errors that require immediate attention
- **WARN:** Potential issues that should be monitored
- **INFO:** General information about system operation
- **DEBUG:** Detailed information for debugging purposes

##### Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "user-service",
  "message": "User created successfully",
  "userId": "12345",
  "requestId": "req_abc123",
  "duration": 150,
  "metadata": {
    "userAgent": "Mozilla/5.0...",
    "ipAddress": "192.168.1.100"
  }
}
```

##### What to Log
- **User Actions:** Important user interactions
- **System Events:** Service starts, stops, configuration changes
- **Errors:** All errors with stack traces and context
- **Performance Metrics:** Response times, resource usage
- **Security Events:** Authentication attempts, authorization failures

#### 10.2 Monitoring Standards

##### Application Metrics
- **Response Times:** Track API and page response times
- **Error Rates:** Monitor error frequency and types
- **Throughput:** Track requests per second and concurrent users
- **Resource Usage:** Monitor CPU, memory, and disk usage

##### Business Metrics
- **User Engagement:** Track user activity and feature usage
- **Conversion Rates:** Monitor business goal completion
- **Performance Impact:** Correlate technical metrics with business outcomes

### 11. Deployment and DevOps Standards

#### 11.1 CI/CD Pipeline

##### Build Process
1. **Code Checkout:** Pull latest code from repository
2. **Dependency Installation:** Install required packages and dependencies
3. **Static Analysis:** Run linting, security scanning, and code quality checks
4. **Unit Tests:** Execute all unit tests with coverage reporting
5. **Integration Tests:** Run integration tests against test environment
6. **Build Artifacts:** Create deployable artifacts (containers, packages)
7. **Security Scanning:** Scan artifacts for vulnerabilities
8. **Deployment:** Deploy to appropriate environment

##### Quality Gates
- **Code Coverage:** Minimum 80% test coverage required
- **Security Scan:** No high or critical vulnerabilities allowed
- **Performance Tests:** Response times within acceptable limits
- **Code Quality:** Meet established quality metrics
- **Manual Approval:** Required for production deployments

#### 11.2 Environment Management

##### Environment Types
- **Development:** Individual developer environments
- **Testing:** Shared testing environment for QA
- **Staging:** Production-like environment for final testing
- **Production:** Live environment serving real users

##### Configuration Management
- **Environment Variables:** Use environment-specific configuration
- **Secrets Management:** Secure handling of sensitive configuration
- **Feature Flags:** Control feature rollout and experimentation
- **Database Migrations:** Automated and reversible schema changes

### 12. Team Collaboration Standards

#### 12.1 Communication Guidelines

##### Daily Standups
- **Format:** What did you do yesterday? What will you do today? Any blockers?
- **Duration:** Maximum 15 minutes
- **Focus:** Progress updates and impediment identification
- **Follow-up:** Schedule separate discussions for complex issues

##### Code Review Communication
- **Respectful Tone:** Maintain professional and constructive communication
- **Specific Feedback:** Provide clear, actionable suggestions
- **Learning Opportunities:** Share knowledge and best practices
- **Timely Response:** Respond to review requests within 24 hours

#### 12.2 Knowledge Sharing

##### Documentation Culture
- **Living Documentation:** Keep documentation up-to-date with code changes
- **Knowledge Base:** Maintain searchable repository of team knowledge
- **Onboarding Materials:** Comprehensive guides for new team members
- **Troubleshooting Guides:** Document common issues and solutions

##### Learning and Development
- **Tech Talks:** Regular presentations on new technologies and techniques
- **Code Reviews:** Use reviews as learning opportunities
- **Pair Programming:** Collaborate on complex problems and knowledge transfer
- **External Learning:** Encourage conference attendance and online courses

### 13. Quality Assurance and Enforcement

#### 13.1 Automated Quality Checks

##### Static Analysis Tools
- **Linting:** Enforce coding style and catch common errors
- **Security Scanning:** Identify potential security vulnerabilities
- **Dependency Checking:** Monitor for vulnerable dependencies
- **Code Complexity:** Measure and limit code complexity
- **Duplication Detection:** Identify and eliminate code duplication

##### Automated Testing
- **Unit Test Execution:** Run all unit tests on every commit
- **Integration Testing:** Execute integration tests on pull requests
- **Performance Testing:** Monitor performance regressions
- **Security Testing:** Automated security vulnerability scanning

#### 13.2 Manual Quality Processes

##### Code Review Requirements
- **Mandatory Reviews:** All code changes require peer review
- **Review Criteria:** Use established checklist for consistent reviews
- **Approval Process:** Require approval from senior developers for critical changes
- **Documentation Review:** Ensure documentation is updated with code changes

##### Quality Metrics
- **Code Coverage:** Track test coverage trends over time
- **Bug Rates:** Monitor defect rates and resolution times
- **Performance Metrics:** Track application performance trends
- **Security Metrics:** Monitor security vulnerability trends

### 14. Continuous Improvement

#### 14.1 Retrospectives

##### Regular Reviews
- **Sprint Retrospectives:** Identify what worked well and what needs improvement
- **Process Evaluation:** Regularly assess and refine development processes
- **Tool Evaluation:** Continuously evaluate and adopt better tools
- **Standards Updates:** Regularly review and update coding standards

##### Metrics-Driven Improvement
- **Performance Monitoring:** Use metrics to identify improvement opportunities
- **Quality Trends:** Track quality metrics to identify patterns
- **Team Feedback:** Gather regular feedback from team members
- **Customer Feedback:** Incorporate user feedback into development practices

#### 14.2 Standards Evolution

##### Update Process
1. **Identify Need:** Recognize when standards need updating
2. **Research Solutions:** Investigate best practices and new approaches
3. **Propose Changes:** Document proposed changes with rationale
4. **Team Review:** Get input and consensus from development team
5. **Pilot Testing:** Test new standards on small projects
6. **Full Adoption:** Roll out successful changes across all projects
7. **Documentation:** Update all relevant documentation

##### Change Management
- **Communication:** Clearly communicate changes to all team members
- **Training:** Provide training on new standards and practices
- **Gradual Adoption:** Phase in changes to minimize disruption
- **Feedback Loop:** Gather feedback and adjust as needed

## Quality Assurance Checklist

Before finalizing the Development Best Practices and Standards Guide, ensure:

### Completeness
- [ ] All major development areas are covered (coding, testing, security, etc.)
- [ ] Language-specific standards are detailed and actionable
- [ ] Architectural guidelines include approved patterns and anti-patterns
- [ ] Security standards address common vulnerabilities
- [ ] Testing standards cover all testing types and levels
- [ ] Version control and code review processes are clearly defined
- [ ] Documentation standards are comprehensive and practical

### Clarity and Actionability
- [ ] All standards include specific, measurable criteria
- [ ] Examples are provided for complex concepts
- [ ] Guidelines are written in clear, unambiguous language
- [ ] Enforcement mechanisms are clearly defined
- [ ] Quality gates and checkpoints are specified

### Technical Accuracy
- [ ] Standards align with selected technology stack
- [ ] Security recommendations follow current best practices
- [ ] Performance guidelines are realistic and measurable
- [ ] Testing strategies are appropriate for project complexity
- [ ] Tool recommendations are current and well-supported

### Team Alignment
- [ ] Standards consider current team skill levels
- [ ] Training requirements are identified and planned
- [ ] Adoption timeline is realistic and achievable
- [ ] Change management process is defined
- [ ] Feedback mechanisms are established

### Enforcement and Monitoring
- [ ] Automated checks are defined where possible
- [ ] Manual review processes are clearly outlined
- [ ] Quality metrics are defined and measurable
- [ ] Reporting and monitoring procedures are established
- [ ] Continuous improvement process is defined

## Target Audience

The primary users of this Development Best Practices and Standards Guide are:

- **Development Team:** Need detailed coding standards and implementation guidelines
- **Code Reviewers:** Need criteria and checklists for effective reviews
- **DevOps Team:** Need CI/CD and deployment standards
- **QA Team:** Need testing standards and quality criteria
- **Project Managers:** Need understanding of quality processes and timelines
- **New Team Members:** Need comprehensive onboarding and reference material

## Output Requirements

- **Format:** Markdown (`.md`)
- **Location:** `/03-Tasks/`
- **Filename:** `development-best-practices-[project-name].md`
- **Length:** Comprehensive guide (typically 20-30 pages)
- **Examples:** Include code examples, templates, and checklists
- **References:** Link to external resources and documentation

## Final Instructions

1. **Be Specific:** Provide concrete, actionable guidelines rather than vague principles
2. **Be Practical:** Consider real-world development constraints and team capabilities
3. **Be Consistent:** Ensure all standards work together cohesively
4. **Be Enforceable:** Define clear criteria that can be objectively measured
5. **Be Adaptable:** Design standards that can evolve with the project and team
6. **Include Examples:** Provide code examples for all major concepts
7. **Consider Automation:** Identify opportunities for automated enforcement
8. **Plan for Adoption:** Consider how standards will be introduced and adopted by the team

This Development Best Practices and Standards Guide serves as the foundation for all development activities and should be treated as a living document that evolves with the project and team capabilities.