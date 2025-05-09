flowchart TD
    subgraph "User Interface Layer"
        UI[User Interface]
        Query[Query Processing]
    end
    
    subgraph "Orchestration Layer"
        Orchestrator[Orchestrator Agent]
    end
    
    subgraph "Specialized Agents"
        StandardsExtractor[Standards Extractor Agent]
        ComplianceValidator[Compliance Validator Agent]
        EnhancementProposer[Enhancement Proposer Agent]
        UseCaseProcessor[Use Case Processor Agent]
        TransactionAnalyzer[Transaction Analyzer Agent]
        ProductDesigner[Product Designer Agent]
        AuditAgent[Audit Agent]
        FraudDetector[Fraud Detection Agent]
        CrossBorderAdvisor[Cross-Border Compliance Agent]
    end
    
    subgraph "Data Layer"
        VectorDB[(Vector Database)]
        KnowledgeBase[(Knowledge Base)]
        AuditTrail[(Audit Trail DB)]
    end
    
    UI --> Query
    Query --> Orchestrator
    
    Orchestrator --> StandardsExtractor
    Orchestrator --> ComplianceValidator
    Orchestrator --> EnhancementProposer
    Orchestrator --> UseCaseProcessor
    Orchestrator --> TransactionAnalyzer
    Orchestrator --> ProductDesigner
    Orchestrator --> AuditAgent
    Orchestrator --> FraudDetector
    Orchestrator --> CrossBorderAdvisor
    
    StandardsExtractor <--> VectorDB
    ComplianceValidator <--> VectorDB
    EnhancementProposer <--> VectorDB
    UseCaseProcessor <--> VectorDB
    TransactionAnalyzer <--> VectorDB
    ProductDesigner <--> VectorDB
    AuditAgent <--> VectorDB
    FraudDetector <--> VectorDB
    CrossBorderAdvisor <--> VectorDB
    
    StandardsExtractor <--> KnowledgeBase
    ComplianceValidator <--> KnowledgeBase
    EnhancementProposer <--> KnowledgeBase
    UseCaseProcessor <--> KnowledgeBase
    TransactionAnalyzer <--> KnowledgeBase
    ProductDesigner <--> KnowledgeBase
    AuditAgent <--> KnowledgeBase
    FraudDetector <--> KnowledgeBase
    CrossBorderAdvisor <--> KnowledgeBase
    
    StandardsExtractor --> AuditTrail
    ComplianceValidator --> AuditTrail
    EnhancementProposer --> AuditTrail
    UseCaseProcessor --> AuditTrail
    TransactionAnalyzer --> AuditTrail
    ProductDesigner --> AuditTrail
    AuditAgent --> AuditTrail
    FraudDetector --> AuditTrail
    CrossBorderAdvisor --> AuditTrail