# Rule: Generating a Technology Stack Analysis Report

## Goal

To guide a CTO Agent in creating a comprehensive Technology Stack Analysis Report in Markdown format, based on an existing Product Requirements Document (PRD) and additional project context. The report should provide a detailed evaluation of available technology options, justify the selection of the most appropriate stack, and ensure professional results within security, efficiency, maintainability, and scalability standards.

## Process

1. **Receive PRD and Context:** The CTO Agent receives the PRD file and any additional project context (budget, timeline, team expertise, existing infrastructure, etc.).
2. **Analyze Requirements:** Extract technical requirements, constraints, and success criteria from the PRD and context.
3. **Research Technology Options:** Identify and evaluate multiple technology stack alternatives that could satisfy the requirements.
4. **Comparative Analysis:** Perform detailed pros/cons analysis for each viable option considering the specific use case.
5. **Make Recommendation:** Select the most appropriate stack with detailed justification.
6. **Generate Report:** Create comprehensive analysis using the structure outlined below.
7. **Save Report:** Save the document as `tech-stack-analysis-[project-name].md` in the `/03-Tasks/` directory.

## Analysis Framework

The CTO Agent must evaluate each technology option across these dimensions:

### Technical Criteria
- **Performance & Scalability:** Response times, throughput, horizontal/vertical scaling capabilities
- **Security:** Built-in security features, vulnerability history, compliance capabilities
- **Maintainability:** Code quality, documentation, debugging tools, refactoring ease
- **Integration:** API compatibility, third-party service integration, existing system compatibility
- **Reliability:** Uptime, error handling, fault tolerance, disaster recovery

### Business Criteria
- **Development Speed:** Time to market, learning curve, development productivity
- **Cost:** Licensing, infrastructure, development, maintenance, operational costs
- **Team Expertise:** Current team skills, training requirements, hiring needs
- **Community & Support:** Documentation quality, community size, commercial support
- **Future-Proofing:** Technology roadmap, vendor stability, migration paths

### Project-Specific Criteria
- **Requirements Alignment:** How well the stack meets specific PRD requirements
- **Constraints Compliance:** Budget, timeline, regulatory, technical constraints
- **Risk Assessment:** Technical risks, vendor lock-in, obsolescence risks

## Report Structure

The generated Technology Stack Analysis Report must include the following sections:

### 1. Executive Summary
- **Recommended Stack:** Clear statement of the selected technology stack
- **Key Justifications:** Top 3-5 reasons for the recommendation
- **Implementation Timeline:** High-level timeline for stack adoption
- **Budget Impact:** Cost implications and ROI projections
- **Risk Assessment:** Major risks and mitigation strategies

### 2. Project Context Analysis
- **PRD Requirements Summary:** Key technical and business requirements extracted from PRD
- **Project Constraints:** Budget, timeline, team, regulatory, and technical constraints
- **Success Criteria:** Measurable objectives the technology stack must support
- **Existing Infrastructure:** Current systems, databases, services that must be considered
- **Team Capabilities:** Current expertise, skills gaps, training needs

### 3. Technology Stack Categories

For each major component category, analyze options:

#### 3.1 Frontend Technology
- **Options Evaluated:** [List 3-5 viable options]
- **Evaluation Matrix:** Detailed comparison table
- **Recommendation:** Selected technology with justification
- **Implementation Considerations:** Setup, configuration, best practices

#### 3.2 Backend Technology
- **Options Evaluated:** [List 3-5 viable options]
- **Evaluation Matrix:** Detailed comparison table
- **Recommendation:** Selected technology with justification
- **Implementation Considerations:** Setup, configuration, best practices

#### 3.3 Database Technology
- **Options Evaluated:** [List 3-5 viable options]
- **Evaluation Matrix:** Detailed comparison table
- **Recommendation:** Selected technology with justification
- **Implementation Considerations:** Setup, configuration, best practices

#### 3.4 Infrastructure & DevOps
- **Options Evaluated:** [List 3-5 viable options]
- **Evaluation Matrix:** Detailed comparison table
- **Recommendation:** Selected technology with justification
- **Implementation Considerations:** Setup, configuration, best practices

#### 3.5 Additional Components
- **Authentication & Authorization:** Identity management solutions
- **Monitoring & Logging:** Observability stack
- **Testing Framework:** Unit, integration, e2e testing tools
- **CI/CD Pipeline:** Continuous integration and deployment tools
- **Security Tools:** Static analysis, vulnerability scanning, secrets management

### 4. Detailed Comparative Analysis

For each technology category, provide detailed analysis using this template:

#### Technology Option: [TECHNOLOGY_NAME]

**Overview:** [Brief description and primary use cases]

**Pros:**
- **[ADVANTAGE_1]:** [Detailed explanation with quantified benefits when possible]
- **[ADVANTAGE_2]:** [Detailed explanation with quantified benefits when possible]
- **[ADVANTAGE_3]:** [Detailed explanation with quantified benefits when possible]

**Cons:**
- **[DISADVANTAGE_1]:** [Detailed explanation with quantified impact when possible]
- **[DISADVANTAGE_2]:** [Detailed explanation with quantified impact when possible]
- **[DISADVANTAGE_3]:** [Detailed explanation with quantified impact when possible]

**Project-Specific Considerations:**
- **Requirements Fit:** How well it meets specific PRD requirements (1-10 scale with justification)
- **Team Readiness:** Current team expertise level (1-10 scale with gap analysis)
- **Implementation Effort:** Estimated setup and development time
- **Operational Complexity:** Ongoing maintenance and operational requirements
- **Cost Analysis:** Development, licensing, infrastructure, and operational costs
- **Risk Assessment:** Technical, business, and operational risks

**Use Case Alignment:**
- **Perfect For:** Scenarios where this technology excels
- **Avoid If:** Situations where this technology is not suitable
- **Migration Path:** How to transition from/to this technology

### 5. Recommended Technology Stack

#### 5.1 Complete Stack Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED STACK                        │
├─────────────────────────────────────────────────────────────┤
│ Frontend:     [SELECTED_FRONTEND_TECH]                     │
│ Backend:      [SELECTED_BACKEND_TECH]                      │
│ Database:     [SELECTED_DATABASE_TECH]                     │
│ Infrastructure: [SELECTED_INFRA_TECH]                      │
│ DevOps:       [SELECTED_DEVOPS_TECH]                       │
│ Monitoring:   [SELECTED_MONITORING_TECH]                   │
│ Security:     [SELECTED_SECURITY_TECH]                     │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2 Architecture Diagram
[Include high-level architecture diagram showing how components interact]

#### 5.3 Justification Matrix

| Criterion | Weight | Score | Weighted Score | Justification |
|-----------|--------|-------|----------------|---------------|
| Performance | 20% | 8/10 | 1.6 | [Specific reasoning] |
| Security | 25% | 9/10 | 2.25 | [Specific reasoning] |
| Maintainability | 15% | 7/10 | 1.05 | [Specific reasoning] |
| Cost | 20% | 6/10 | 1.2 | [Specific reasoning] |
| Team Fit | 10% | 8/10 | 0.8 | [Specific reasoning] |
| Scalability | 10% | 9/10 | 0.9 | [Specific reasoning] |
| **Total** | **100%** | - | **7.8/10** | **Strong Recommendation** |

### 6. Implementation Roadmap

#### Phase 1: Foundation Setup (Weeks 1-X)
- [ ] **Infrastructure Setup:** [Specific tasks and timeline]
- [ ] **Development Environment:** [Specific tasks and timeline]
- [ ] **CI/CD Pipeline:** [Specific tasks and timeline]
- [ ] **Security Baseline:** [Specific tasks and timeline]

#### Phase 2: Core Development (Weeks X-Y)
- [ ] **Backend Services:** [Specific tasks and timeline]
- [ ] **Database Setup:** [Specific tasks and timeline]
- [ ] **API Development:** [Specific tasks and timeline]
- [ ] **Authentication System:** [Specific tasks and timeline]

#### Phase 3: Frontend & Integration (Weeks Y-Z)
- [ ] **Frontend Application:** [Specific tasks and timeline]
- [ ] **System Integration:** [Specific tasks and timeline]
- [ ] **Testing Implementation:** [Specific tasks and timeline]
- [ ] **Performance Optimization:** [Specific tasks and timeline]

#### Phase 4: Production Readiness (Weeks Z-W)
- [ ] **Security Hardening:** [Specific tasks and timeline]
- [ ] **Monitoring Setup:** [Specific tasks and timeline]
- [ ] **Documentation:** [Specific tasks and timeline]
- [ ] **Deployment & Go-Live:** [Specific tasks and timeline]

### 7. Risk Analysis & Mitigation

#### High-Risk Areas

##### Risk 1: [RISK_NAME]
- **Description:** [Detailed risk description]
- **Probability:** [High/Medium/Low] ([X]%)
- **Impact:** [Critical/High/Medium/Low]
- **Risk Score:** [Probability × Impact]
- **Mitigation Strategy:** [Specific actions to prevent/reduce risk]
- **Contingency Plan:** [What to do if risk materializes]
- **Monitoring Indicators:** [Early warning signs]
- **Owner:** [Responsible team/person]

#### Medium-Risk Areas
[Use same structure as high-risk areas]

#### Low-Risk Areas
[Use same structure as high-risk areas]

### 8. Cost Analysis

#### Development Costs
- **Licensing:** [Annual/one-time costs for all tools and platforms]
- **Infrastructure:** [Cloud/hosting costs with scaling projections]
- **Development Team:** [Team size × duration × rates]
- **Training:** [Upskilling costs for new technologies]
- **Third-party Services:** [APIs, SaaS tools, external services]

#### Operational Costs (Annual)
- **Infrastructure Maintenance:** [Ongoing hosting and infrastructure costs]
- **Licensing Renewals:** [Annual software licensing costs]
- **Support & Maintenance:** [Team costs for ongoing maintenance]
- **Monitoring & Security:** [Operational security and monitoring costs]
- **Scaling Costs:** [Additional costs as system grows]

#### Cost Comparison
| Stack Option | Year 1 | Year 2 | Year 3 | 3-Year Total | TCO per User |
|--------------|--------|--------|--------|--------------|--------------|
| Recommended | €X | €Y | €Z | €Total | €PerUser |
| Alternative 1 | €X | €Y | €Z | €Total | €PerUser |
| Alternative 2 | €X | €Y | €Z | €Total | €PerUser |

### 9. Performance & Scalability Projections

#### Performance Benchmarks
- **Response Time:** [Expected API response times under various loads]
- **Throughput:** [Transactions per second capacity]
- **Concurrent Users:** [Maximum concurrent users supported]
- **Data Volume:** [Maximum data volume handling capacity]
- **Availability:** [Expected uptime percentage]

#### Scalability Plan
- **Horizontal Scaling:** [How to add more servers/instances]
- **Vertical Scaling:** [How to increase server capacity]
- **Database Scaling:** [Sharding, replication, clustering strategies]
- **CDN Strategy:** [Content delivery and caching approach]
- **Load Balancing:** [Traffic distribution strategy]

#### Growth Projections
| Metric | Month 1 | Month 6 | Year 1 | Year 2 | Year 3 |
|--------|---------|---------|--------|--------|--------|
| Users | X | Y | Z | A | B |
| Requests/day | X | Y | Z | A | B |
| Data Volume | X GB | Y GB | Z GB | A TB | B TB |
| Infrastructure Cost | €X | €Y | €Z | €A | €B |

### 10. Security & Compliance Framework

#### Security Architecture
- **Authentication:** [Multi-factor authentication, SSO integration]
- **Authorization:** [Role-based access control, permissions model]
- **Data Encryption:** [At rest and in transit encryption standards]
- **Network Security:** [Firewalls, VPNs, network segmentation]
- **Application Security:** [Input validation, SQL injection prevention, XSS protection]

#### Compliance Requirements
- **GDPR:** [Data protection and privacy measures]
- **SOC 2:** [Security controls and audit requirements]
- **ISO 27001:** [Information security management system]
- **Industry-Specific:** [HIPAA, PCI-DSS, etc. if applicable]

#### Security Monitoring
- **SIEM Integration:** [Security information and event management]
- **Vulnerability Scanning:** [Automated security testing]
- **Penetration Testing:** [Regular security assessments]
- **Incident Response:** [Security incident handling procedures]

### 11. Team Readiness & Training Plan

#### Current Team Assessment
| Team Member | Role | Current Skills | Required Skills | Gap Analysis | Training Plan |
|-------------|------|----------------|-----------------|--------------|---------------|
| [Name] | [Role] | [Skills] | [Skills] | [Gap] | [Training] |

#### Training Requirements
- **Technology-Specific Training:** [Courses, certifications, workshops needed]
- **Timeline:** [Training schedule aligned with project phases]
- **Budget:** [Training costs and resource allocation]
- **Success Metrics:** [How to measure training effectiveness]

#### Knowledge Transfer Plan
- **Documentation:** [Technical documentation requirements]
- **Mentoring:** [Senior-junior developer pairing]
- **Code Reviews:** [Knowledge sharing through code review process]
- **Best Practices:** [Coding standards and architectural guidelines]

### 12. Alternative Scenarios

#### Scenario A: Budget Constraints
- **Modified Stack:** [Cost-optimized technology choices]
- **Trade-offs:** [What capabilities are sacrificed]
- **Migration Path:** [How to upgrade later when budget allows]

#### Scenario B: Accelerated Timeline
- **Modified Stack:** [Faster-to-implement technology choices]
- **Trade-offs:** [What long-term benefits are sacrificed]
- **Technical Debt:** [Future refactoring requirements]

#### Scenario C: Team Constraints
- **Modified Stack:** [Technology choices matching current team skills]
- **Trade-offs:** [What advanced capabilities are postponed]
- **Skill Development:** [Gradual team upskilling plan]

### 13. Success Metrics & KPIs

#### Technical KPIs
- **Performance:** [Response time, throughput, availability targets]
- **Quality:** [Bug rates, test coverage, code quality metrics]
- **Security:** [Vulnerability counts, security incident frequency]
- **Maintainability:** [Code complexity, documentation coverage]

#### Business KPIs
- **Time to Market:** [Development velocity, feature delivery speed]
- **Cost Efficiency:** [Development cost per feature, operational cost per user]
- **Team Productivity:** [Story points per sprint, feature completion rate]
- **User Satisfaction:** [Performance perception, feature adoption rate]

#### Monitoring & Reporting
- **Dashboard:** [Real-time metrics visualization]
- **Reporting Frequency:** [Daily, weekly, monthly reports]
- **Stakeholder Communication:** [Regular updates to leadership]
- **Continuous Improvement:** [Regular stack evaluation and optimization]

## Quality Assurance Checklist

Before finalizing the Technology Stack Analysis Report, ensure:

### Completeness
- [ ] All technology categories have been evaluated
- [ ] At least 3 viable options analyzed for each major component
- [ ] Detailed pros/cons provided for each option
- [ ] Clear recommendation with quantified justification
- [ ] Implementation roadmap with realistic timelines
- [ ] Comprehensive risk analysis with mitigation strategies
- [ ] Detailed cost analysis with 3-year projections

### Technical Accuracy
- [ ] Technology capabilities accurately represented
- [ ] Performance claims backed by benchmarks or credible sources
- [ ] Security considerations thoroughly addressed
- [ ] Scalability projections based on realistic assumptions
- [ ] Integration challenges properly identified

### Business Alignment
- [ ] Recommendations align with PRD requirements
- [ ] Budget constraints properly considered
- [ ] Timeline constraints realistically addressed
- [ ] Team capabilities honestly assessed
- [ ] ROI projections are conservative and achievable

### Actionability
- [ ] Implementation steps are specific and measurable
- [ ] Resource requirements clearly defined
- [ ] Dependencies and prerequisites identified
- [ ] Success criteria are measurable
- [ ] Risk mitigation plans are actionable

## Target Audience

The primary readers of this Technology Stack Analysis Report are:

- **Project Stakeholders:** Need executive summary and business justification
- **Development Team:** Need technical details and implementation guidance
- **DevOps Team:** Need infrastructure and operational requirements
- **Security Team:** Need security architecture and compliance information
- **Budget Owners:** Need cost analysis and ROI projections

## Output Requirements

- **Format:** Markdown (`.md`)
- **Location:** `/03-Tasks/`
- **Filename:** `tech-stack-analysis-[project-name].md`
- **Length:** Comprehensive analysis (typically 15-25 pages)
- **Diagrams:** Include architecture diagrams, decision trees, comparison matrices
- **Data:** Include quantified analysis wherever possible

## Final Instructions

1. **Be Thorough:** This analysis will guide major technical decisions for the entire project
2. **Be Objective:** Present balanced analysis even if one option is clearly superior
3. **Be Specific:** Avoid generic statements; provide project-specific insights
4. **Be Practical:** Consider real-world constraints and implementation challenges
5. **Be Forward-Looking:** Consider long-term implications and evolution paths
6. **Validate Assumptions:** Clearly state assumptions and validate them when possible
7. **Update Regularly:** Technology landscapes change; plan for periodic reviews

This Technology Stack Analysis Report serves as the technical foundation for all subsequent development decisions and should be treated as a living document that evolves with the project.