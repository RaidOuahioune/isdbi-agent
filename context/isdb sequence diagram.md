sequenceDiagram
    participant User
    participant UI as User Interface
    participant Orch as Orchestrator Agent
    participant Agents as Specialized Agents
    participant VDB as Vector Database
    participant KB as Knowledge Base
    participant AT as Audit Trail

    User->>UI: Submit query/request
    UI->>Orch: Process and route query
    
    Orch->>Orch: Determine query type and required agents
    
    Orch->>Agents: Assign primary and secondary agents
    
    Agents->>VDB: Retrieve relevant standard embeddings
    VDB-->>Agents: Return relevant data
    
    Agents->>KB: Query structured knowledge
    KB-->>Agents: Return applicable rules and guidelines
    
    Agents->>Agents: Process information and generate response
    
    alt Standard Enhancement Flow
        Agents->>Orch: Extract key elements from standard
        Orch->>Agents: Request enhancement proposals
        Agents->>Agents: Generate enhancement proposals
        Agents->>Orch: Submit proposals
        Orch->>Agents: Request validation of proposals
        Agents->>Agents: Validate against Shariah principles
        Agents->>Orch: Provide validation results
    end
    
    alt Use Case Scenario Flow
        Agents->>Orch: Analyze financial scenario
        Orch->>Agents: Request applicable standards
        Agents->>Agents: Identify relevant standards
        Agents->>Orch: Provide accounting guidance
        Orch->>Agents: Request journal entries
        Agents->>Agents: Generate compliant entries
        Agents->>Orch: Submit accounting solution
    end
    
    alt Reverse Transaction Flow
        Agents->>Orch: Analyze transaction entries
        Orch->>Agents: Request standard identification
        Agents->>Agents: Determine applicable standards
        Agents->>Orch: Rank standards by relevance
        Orch->>Agents: Request justification
        Agents->>Agents: Generate reasoning
        Agents->>Orch: Submit standard rankings with justification
    end
    
    alt Custom Category Flow
        Agents->>Orch: Process specialized request
        Orch->>Agents: Coordinate multi-agent response
        Agents->>Agents: Collaborate on solution
        Agents->>Orch: Submit integrated solution
    end
    
    Agents->>AT: Log actions and reasoning
    
    Agents->>Orch: Return processed results
    Orch->>UI: Format and display comprehensive response
    UI->>User: Present solution with explanations