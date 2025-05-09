graph TD
    subgraph "Phase 1: Standards Analysis"
        A1[Extractor Agent] -->|Parse Standard| B1[Extract Key Elements]
        B1 -->|Identify Core Rules| C1[Create Structured Representation]
        C1 -->|Map Relationships| D1[Identify Ambiguities/Gaps]
    end
    
    subgraph "Phase 2: Enhancement Generation"
        A2[Enhancement Proposer] -->|Analyze Standard Elements| B2[Generate Improvement Ideas]
        B2 -->|Draft Specific Changes| C2[Provide Rationale]
        C2 -->|Structure Proposal| D2[Tag with References]
    end
    
    subgraph "Phase 3: Shariah Validation"
        A3[Compliance Validator] -->|Review Proposed Changes| B3[Check Shariah Compliance]
        B3 -->|Cross-reference Sources| C3[Evaluate Practical Impact]
        C3 -->|Apply Fiqh Principles| D3[Provide Validation Result]
    end
    
    subgraph "Phase 4: Impact Analysis"
        A4[Product Designer] -->|Analyze Proposed Changes| B4[Simulate Application to Products]
        B4 -->|Identify Implementation Challenges| C4[Suggest Transition Approach]
        A4 -->|Check Industry Practice| D4[Compare with Global Standards]
    end
    
    subgraph "Phase 5: Final Recommendation"
        A5[Orchestrator] -->|Consolidate Inputs| B5[Rank Enhancement Options]
        B5 -->|Format Final Report| C5[Include All Reasoning]
        C5 -->|Provide Implementation Path| D5[Present to User]
    end
    
    D1 --> A2
    D2 --> A3
    D3 --> A4
    D4 --> A5
    D5 --> Final[Final Enhanced Standard]