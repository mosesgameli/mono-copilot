"""
Product Engineer Skill - PRD Generation with Web Search + Architecture Design + Exception Management.

Takes approved BRD and transforms into technical PRD with:
- Architectural impact analysis (technology stack, feasibility assessment)
- Design considerations (design thinking, user experience, system interactions)
- Integration architecture (explicit protocols, APIs, failure handling per integration)
- Technical architecture (components, microservices, data models)
- Exception management (failure scenarios, detection, recovery, escalation)
- Non-functional requirements (performance, availability, security, scalability)
- Rollback strategy (disaster recovery, fallback options)
- Mermaid diagrams (system architecture, integration flows, exception handling)

Uses OpenAI web_search_20250305 for technology validation and best practices.
Integrates ResearchService for verifying technology choices and integration patterns.
Generates Mermaid diagrams based on architecture complexity.
"""

from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path
import os
import re
from openai import AsyncOpenAI

from ..services.research_service import ResearchService


class PESkill:
    """PE Skill - Technical PRD generation with architecture design and exception management."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo"
        self.research_service = ResearchService()
    
    def _system_prompt(self) -> str:
        """
        System prompt for PE workflow with web search and architecture instructions.
        Focus: Technical feasibility, integration architecture, non-functional requirements.
        
        CRITICAL: Instructs agent to validate technology choices and integration patterns.
        """
        return """You are a Product Engineer for enterprise MNO systems (Nigeria, Ghana, Kenya, South Africa, Egypt).

YOUR PE PROCESS (Building on BA's BRD):

1. ARCHITECTURAL IMPACT ANALYSIS
   Assess what the BA proposed:
   - Technology feasibility: Can we build this? With what tech stack?
   - System interactions: Which systems must change behavior?
   - Infrastructure implications: New compute, storage, networking needed?
   - Integration impact: How many new integration points? Complexity level?
   - Team impact: Do we need new skills? Training required?
   Example: "BA proposed AI recommendation engine. Feasible via cloud ML platform (AWS SageMaker, Azure ML). Requires Python/Scala teams."

2. DESIGN CONSIDERATIONS
   Design thinking applied to requirements:
   - User experience: How will customers/agents interact with solution?
   - System usability: Will operators understand new system behavior?
   - Failure gracefully: What happens when components fail?
   - Monitoring visibility: Can we see what's happening in production?
   - Security posture: What data is at risk? How do we protect it?
   Example: "Agent portal must show recommendations within 2 seconds. UI shows 'Loading...' if delayed. Red indicator if failed."

3. INTEGRATION ARCHITECTURE (CRITICAL FOR LARGE-SCALE)
   For EACH integration from BA, specify:
   - Source system (e.g., CRM)
   - Target system (e.g., AI Engine)
   - Protocol: REST API / message queue / real-time sync / database sync
   - Latency requirement: e.g., "< 2 seconds"
   - Data format: JSON / XML / binary
   - Authentication: API key / OAuth / mTLS
   - Failure handling: Detection → Recovery → Escalation
   - Example:
     CRM → AI Engine: REST API, < 2 sec latency, JSON, API key auth
     Failure: Timeout > 5s → Use cached data + rule-based fallback → Log incident → Alert ML team

4. TECHNICAL ARCHITECTURE
   System design at component level:
   - Components: Frontend (NextJS), Backend (Python FastAPI), Database (PostgreSQL), Cache (Redis)
   - Microservices: Which services? Responsibilities? Communication patterns?
   - Data models: User, Customer, Recommendation, Transaction schemas with audit fields
   - APIs: Endpoint definitions, request/response formats, error codes
   - Real-time: WebSocket connections, event streaming, messaging queues
   - Storage: Database design, backup strategy, replication

5. EXCEPTION MANAGEMENT (CRITICAL FOR 99.9% UPTIME)
   For each failure scenario, specify:
   - Detection: How do we know it failed? What metric/log?
   - User impact: What does customer/agent see/experience?
   - Recovery: Immediate action to keep system running
   - System action: Automated remediation (retry, failover, circuit breaker)
   - Monitoring: What alert fires? To whom? When?
   - Root cause analysis: How do ops investigate?
   
   Example:
   - Database connection pool exhausted
     Detection: Connection timeout > 30 seconds
     Impact: API calls reject with 503, users see "System busy, retry later"
     Recovery: Auto-scale DB connections, kill idle connections
     System: Circuit breaker opens, routes to read-only replica
     Monitoring: Alert to DB team within 1 minute
     RCA: Check for connection leaks in code, review recent deployments

6. NON-FUNCTIONAL REQUIREMENTS (CRITICAL)
   Define measurable SLAs for large-scale MNO:
   - Performance: API latency p95 < 500ms, database query p95 < 100ms
   - Availability: 99.9% uptime SLA, RTO 15min, RPO 5min
   - Scalability: Support 10x current load, auto-scale based on metrics
   - Security: AES-256 encryption at rest, TLS 1.3 in transit, role-based access
   - Compliance: NCC/NCA/ICASA regulations, data residency, retention policies
   - Audit: Every state-changing operation logged with who/what/when/why
   - Monitoring: 5 layers (infrastructure/app/network/database/business metrics)
   - Data quality: Reconciliation jobs verify data integrity daily

7. ROLLBACK STRATEGY
   If PRD fails in production:
   - Rollback plan: How to revert to previous version?
   - Data recovery: How to recover corrupted data?
   - Customer notification: How to communicate outage?
   - Fallback service: What takes over if system is down?
   - Recovery testing: How often do we test disaster recovery?
   Example: "Blue-green deployment. Database migrations versioned. 15-min rollback SLA."

8. MERMAID DIAGRAMS (Based on Architecture Complexity)
   Generate if system has:
   - >2 integrations: System architecture diagram (boxes for systems, arrows for APIs)
   - >3 components: Microservices diagram (services, communication patterns)
   - >2 failure points: Exception handling decision tree (detection → recovery paths)
   - Data movement: Integration flow diagram (data source → processing → destination)

OUTPUT SECTIONS (Markdown PRD):

# PRD: [Solution Title]

## Executive Summary
Problem solved, proposed solution, expected business outcomes

## Architectural Impact Analysis
Technology feasibility, system interactions, infrastructure implications

## Design Considerations
UX design, system usability, failure handling, monitoring, security

## Integration Architecture
For each integration: system A ↔ system B, protocol, latency, data format, auth, failure handling

## Technical Architecture
Components, microservices, data models, APIs, real-time mechanisms, storage

## Exception Management
For each failure: detection, user impact, recovery, system action, monitoring, RCA

## Non-Functional Requirements
Performance SLAs, availability targets, scalability, security controls, compliance, audit, monitoring

## Rollback Strategy
Rollback procedures, data recovery, customer communication, fallback service, testing

## Implementation Roadmap
Phase 1 (weeks 1-4): Core APIs, database
Phase 2 (weeks 5-8): Integrations
Phase 3 (weeks 9-12): Testing, hardening
Phase 4 (weeks 13+): Production deployment

QUALITY STANDARDS FOR LARGE-SCALE MNO:
- All integrations MUST specify protocol, latency, authentication, failure handling
- All NFRs MUST be measurable SLAs (not "fast", but "p95 < 500ms")
- All exceptions MUST have detection method, impact, recovery, monitoring
- All compliance requirements MUST be specific (not "secure", but "AES-256, TLS 1.3")
- All architecture MUST handle 99.9% uptime requirement
- All technology choices MUST be validated against current best practices
- Mermaid diagrams ONLY when architecture complexity warrants them

BE SPECIFIC. BE MEASURABLE. BE IMPLEMENTABLE. BE RESILIENT."""
    
    async def generate_prd(
        self,
        brd_dict: Dict,
        clarification_feedback: Optional[str] = None,
        run_count: int = 1
    ) -> Dict:
        """
        Generate PRD from approved BRD.
        
        Takes BA output and transforms into technical requirements.
        Uses web search to validate technology choices and integration patterns.
        Integrates ResearchService for verifying architectural patterns.
        Smart Mermaid diagram generation based on system complexity.
        """
        
        try:
            document_id = f"PRD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            brd_reference = brd_dict.get("document_id", "BRD-unknown")
            
            user_prompt = self._build_user_prompt(brd_dict, clarification_feedback, run_count)
            
            # Call OpenAI with web_search tool enabled
            response = await self.client.chat.completions.create(
                model=self.model,
                max_tokens=4500,
                tools=[
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "description": "Search for technology best practices, architecture patterns, integration standards, and MNO compliance requirements"
                    }
                ],
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract markdown from response
            markdown = self._extract_markdown_from_response(response)
            
            if not markdown:
                return {
                    "status": "error",
                    "document_id": None,
                    "error": "Failed to extract PRD content from response",
                    "markdown": None,
                    "quality_gates_passed": False
                }
            
            # Determine if Mermaid diagrams needed based on architecture complexity
            needs_mermaid = self._should_generate_architecture_diagrams(brd_dict, markdown)
            
            # Check quality gates (5 mandatory gates for PRD)
            quality_gates = self._check_quality_gates(markdown, brd_dict, needs_mermaid)
            
            # Extract and verify sources from PRD
            sources_metadata = await self._extract_and_verify_sources(
                markdown,
                brd_dict.get("structured", {})
            )
            
            # Add verified sources as footnotes
            enhanced_markdown = self._add_verified_footnotes(markdown, sources_metadata)
            
            # Validate Mermaid syntax if present
            if needs_mermaid and "```mermaid" in enhanced_markdown:
                quality_gates["mermaid_diagrams"] = self._validate_mermaid_syntax(enhanced_markdown)
            else:
                quality_gates["mermaid_diagrams"] = not needs_mermaid  # Pass if not needed
            
            # Save outputs
            Path("projects").mkdir(exist_ok=True)
            prd_path = Path("projects") / "prd.md"
            prd_path.write_text(enhanced_markdown)
            
            sources_path = Path("projects") / "sources-prd.json"
            sources_path.write_text(json.dumps(sources_metadata, indent=2, default=str))
            
            # Determine overall quality gate pass
            mandatory_gates = [
                quality_gates.get("workflows_concrete", False),
                quality_gates.get("features_map_to_metrics", False),
                quality_gates.get("acceptance_criteria_testable", False),
                quality_gates.get("constraints_visible", False),
                quality_gates.get("scope_realistic", False)
            ]
            gates_passed = all(mandatory_gates)
            
            return {
                "status": "success",
                "document_id": document_id,
                "brd_reference": brd_reference,
                "markdown": enhanced_markdown,
                "structured": self._parse_sections(markdown),
                "sources_metadata": sources_metadata,
                "quality_gates": quality_gates,
                "quality_gates_passed": gates_passed,
                "approval_required": True,
                "generated_at": datetime.now().isoformat(),
                "run_count": run_count,
                "file_path": str(prd_path),
                "sources_verified_count": len(sources_metadata.get("sources_used", []))
            }
        
        except Exception as e:
            return {
                "status": "error",
                "document_id": None,
                "error": str(e),
                "markdown": None,
                "quality_gates_passed": False
            }
    
    def _build_user_prompt(
        self,
        brd_dict: Dict,
        feedback: Optional[str],
        run_count: int
    ) -> str:
        """Build prompt with approved BRD as context."""
        
        brd_markdown = brd_dict.get("markdown", "")
        brd_id = brd_dict.get("document_id", "BRD-unknown")
        
        prompt = f"""BRD REFERENCE: {brd_id}

APPROVED BUSINESS REQUIREMENTS:
{brd_markdown[:3000]}...  [BRD continues, see above for full context]

YOUR TASK:
Transform this approved BRD into a comprehensive PRD with:

1. **Architectural Impact Analysis**
   - Technology stack options and recommendations
   - System interaction changes required
   - Infrastructure implications
   - Feasibility assessment

2. **Design Considerations**
   - User experience for customers and agents
   - System usability and monitoring
   - Graceful failure handling
   - Security posture

3. **Integration Architecture**
   - For EACH integration mentioned in BRD:
     * Source/target systems
     * Protocol (REST/message queue/sync)
     * Latency requirements
     * Authentication method
     * Failure detection + recovery

4. **Technical Architecture**
   - Components and microservices
   - Data models with audit fields
   - API endpoints
   - Storage and caching strategy

5. **Exception Management**
   - For each failure scenario: detection, impact, recovery, monitoring
   - 99.9% uptime strategy
   - Disaster recovery procedures

6. **Non-Functional Requirements**
   - Performance SLAs (measurable: p95 latency, throughput)
   - Availability targets (99.9% uptime, RTO, RPO)
   - Security standards (encryption, TLS, RBAC)
   - Compliance requirements (NCC/NCA/ICASA)
   - Audit and monitoring requirements

7. **Rollback Strategy**
   - How to revert if deployment fails
   - Data recovery procedures
   - Fallback services

8. **Mermaid Diagrams**
   - System architecture (if >2 integrations)
   - Exception handling decision trees (if complex)
   - Data flow diagrams (if data movement critical)
"""
        
        if feedback and run_count > 1:
            prompt += f"\nREFINEMENT FEEDBACK (Attempt {run_count}):\n{feedback}\n"
        
        prompt += """
QUALITY STANDARDS:
- All technology choices validated against current best practices
- All NFRs are measurable SLAs (not vague terms)
- All integrations specify protocol, latency, authentication, failure handling
- All exceptions have detection, impact, recovery, monitoring strategy
- Compliance explicitly tied to regulatory bodies (NCC, NCA, CMA, ICASA, NTRA)
- Architecture supports 99.9% uptime requirement
- Mermaid diagrams only if complexity warrants
- All metrics specific (not "fast", but "< 500ms p95")
"""
        
        return prompt
    
    def _extract_markdown_from_response(self, response) -> Optional[str]:
        """Extract markdown from OpenAI response."""
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content
        
        return None
    
    def _should_generate_architecture_diagrams(
        self,
        brd_dict: Dict,
        markdown: str
    ) -> bool:
        """
        Determine if architecture diagrams should be generated.
        
        Criteria:
        - >2 system integrations (generate system architecture)
        - >3 microservices mentioned (generate services diagram)
        - Complex exception flows (generate exception decision tree)
        - Multi-layer architecture (frontend, backend, database, cache)
        """
        
        text = (markdown + " " + brd_dict.get("markdown", "")).lower()
        
        # Count integration complexity indicators
        integration_keywords = ["api", "integration", "crm", "ivr", "database", "queue", "cache", "elasticsearch"]
        integration_count = sum(1 for kw in integration_keywords if kw in text)
        
        # Count architecture layers
        architecture_keywords = ["frontend", "backend", "database", "cache", "microservice", "container", "docker"]
        architecture_count = sum(1 for kw in architecture_keywords if kw in text)
        
        # Count exception/resilience mentions
        resilience_keywords = ["exception", "failure", "timeout", "retry", "failover", "recovery", "circuit breaker"]
        resilience_count = sum(1 for kw in resilience_keywords if kw in text)
        
        # Integration count from BRD
        brd_integrations = brd_dict.get("structured", {}).get("Integration Architecture", "")
        if brd_integrations:
            brd_integration_count = len(re.findall(r'[\w\s]+→|↔', brd_integrations))
        else:
            brd_integration_count = 0
        
        # Trigger diagrams if complexity warrants
        needs_diagram = (
            integration_count >= 2 or
            brd_integration_count > 2 or
            architecture_count >= 2 or
            resilience_count >= 3 or
            "microservice" in text or
            "distributed" in text
        )
        
        return needs_diagram
    
    def _check_quality_gates(
        self,
        markdown: str,
        brd_dict: Dict,
        needs_mermaid: bool
    ) -> Dict[str, bool]:
        """
        Check quality gates specific to PRD.
        5 mandatory gates for Product Requirements.
        """
        
        text = markdown.lower()
        lines = markdown.split('\n')
        
        # 1. Workflows Concrete: describes step-by-step flows with specific systems/actors
        workflows = (
            ("workflow" in text or "process" in text or "flow" in text) and
            any(re.search(r'(user|system|actor|component|service|api|database)', line, re.IGNORECASE) for line in lines)
        )
        
        # 2. Features Map to Metrics: each requirement ties to measurable outcome
        features_metrics = (
            any(re.search(r'(sla|latency|throughput|availability|performance|response time)', line, re.IGNORECASE) for line in lines) and
            any(re.search(r'\d+\s*(ms|second|percent|%|rps|calls)', line, re.IGNORECASE) for line in lines)
        )
        
        # 3. Acceptance Criteria Testable: criteria are specific and verifiable
        acceptance = (
            ("acceptance" in text or "must" in text or "should" in text or "shall" in text) and
            any(re.search(r'(verify|test|validate|check|assert|confirm)', line, re.IGNORECASE) for line in lines)
        )
        
        # 4. Constraints Visible: technical/resource/compliance constraints are explicit
        constraints = (
            ("constraint" in text or "limit" in text or "requirement" in text or "compliance" in text or "ncc\|nca\|cma" in text) and
            any(re.search(r'(maximum|minimum|must not|required|cannot|limited)', line, re.IGNORECASE) for line in lines)
        )
        
        # 5. Scope Realistic: timeline/effort/resources are realistic for the scope
        scope = (
            ("scope" in text or "timeline" in text or "phase" in text or "week" in text or "month" in text) and
            any(re.search(r'(phase|week|month|iteration|sprint|deliverable)', line, re.IGNORECASE) for line in lines)
        )
        
        # Mermaid diagrams
        mermaid = not needs_mermaid or "```mermaid" in markdown
        
        return {
            "workflows_concrete": workflows,
            "features_map_to_metrics": features_metrics,
            "acceptance_criteria_testable": acceptance,
            "constraints_visible": constraints,
            "scope_realistic": scope,
            "mermaid_diagrams": mermaid
        }
    
    async def _extract_and_verify_sources(
        self,
        markdown: str,
        brd_structured: Dict
    ) -> Dict:
        """
        Extract and verify technology/architecture sources from PRD.
        Validate against best practices and compliance standards.
        """
        
        sources_used = []
        
        # Search for technology recommendations and validate them
        tech_keywords = ["python", "fastapi", "postgresql", "redis", "kubernetes", "docker", "tls", "aes", "aws", "azure"]
        compliance_keywords = ["ncc", "nca", "cma", "icasa", "ntra", "gdpr", "compliance", "encryption"]
        
        text_lower = markdown.lower()
        
        # Verify technology mentions
        for keyword in tech_keywords:
            if keyword in text_lower:
                search_result = await self.research_service.search_and_verify(keyword)
                if search_result.get("verified_sources"):
                    for source in search_result["verified_sources"]:
                        if source not in sources_used:
                            sources_used.append(source)
        
        # Verify compliance mentions
        for keyword in compliance_keywords:
            if keyword in text_lower:
                search_result = await self.research_service.search_and_verify(keyword)
                if search_result.get("verified_sources"):
                    for source in search_result["verified_sources"]:
                        if source not in sources_used:
                            sources_used.append(source)
        
        # Extract key architectural decisions from markdown
        architecture_section = ""
        for section_name, section_content in {"Technical Architecture": ""}.items():
            if section_name.lower() in text_lower:
                architecture_section = section_content
        
        # Build sources metadata
        sources_metadata = {
            "prd_id": f"PRD-{datetime.now().strftime('%Y%m%d')}",
            "generated_at": datetime.now().isoformat(),
            "sources_used": sources_used,
            "architecture_decisions": {
                "technology_stack": self._extract_tech_choices(markdown),
                "integration_patterns": self._extract_integration_patterns(markdown),
                "compliance_references": self._extract_compliance_refs(markdown)
            },
            "search_statistics": {
                "total_searches": len(tech_keywords + compliance_keywords),
                "sources_verified": len(sources_used),
                "verification_coverage": "high" if len(sources_used) >= 3 else "medium" if len(sources_used) >= 1 else "low"
            },
            "data_integrity": {
                "all_sources_verified": len(sources_used) >= 3,
                "hallucination_risk": "low" if len(sources_used) >= 3 else "medium" if len(sources_used) >= 1 else "high",
                "technology_choices_validated": len(sources_used) >= 1,
                "manual_review_recommended": len(sources_used) == 0
            }
        }
        
        return sources_metadata
    
    def _extract_tech_choices(self, markdown: str) -> List[str]:
        """Extract technology choices from PRD."""
        tech_keywords = ["python", "fastapi", "postgresql", "redis", "kubernetes", "docker", "nextjs", "react"]
        choices = []
        for tech in tech_keywords:
            if tech in markdown.lower():
                choices.append(tech)
        return choices
    
    def _extract_integration_patterns(self, markdown: str) -> List[str]:
        """Extract integration patterns mentioned."""
        patterns = []
        for pattern in ["rest api", "graphql", "message queue", "event streaming", "real-time sync"]:
            if pattern in markdown.lower():
                patterns.append(pattern)
        return patterns
    
    def _extract_compliance_refs(self, markdown: str) -> List[str]:
        """Extract compliance/regulatory references."""
        refs = []
        for ref in ["ncc", "nca", "cma", "icasa", "ntra"]:
            if ref in markdown.lower():
                refs.append(ref.upper())
        return list(set(refs))
    
    def _add_verified_footnotes(self, markdown: str, sources_metadata: Dict) -> str:
        """Add verified references section with architecture decision tracing."""
        
        sources = sources_metadata.get("sources_used", [])
        
        if not sources:
            return markdown + "\n\n## Architecture Decision References\n\n**Note:** Technology choices were not verified against external sources. Manual architecture review recommended.\n"
        
        references = "\n\n## Architecture Decision References\n\n"
        
        for idx, source in enumerate(sources, 1):
            authority = source.get("authority_level", "unknown").upper()
            confidence = source.get("confidence_level", "unknown").upper()
            accessed = source.get("accessed_at", "N/A")
            claim = source.get("claim", "N/A")
            url = source.get("source_url", "N/A")
            
            references += f"[{idx}] **{claim}**\n"
            references += f"- Source: {url}\n"
            references += f"- Authority: {authority} | Confidence: {confidence}\n"
            references += f"- Verified: {accessed}\n"
            references += f"- Type: {source.get('source_type', 'N/A')}\n\n"
        
        # Add architecture decision summary
        architecture = sources_metadata.get("architecture_decisions", {})
        references += "---\n\n**Technology Stack**\n"
        for tech in architecture.get("technology_stack", []):
            references += f"- {tech.upper()}\n"
        
        references += "\n**Integration Patterns**\n"
        for pattern in architecture.get("integration_patterns", []):
            references += f"- {pattern}\n"
        
        references += "\n**Compliance References**\n"
        for ref in architecture.get("compliance_references", []):
            references += f"- {ref}\n"
        
        # Data integrity summary
        references += "\n---\n\n**Data Integrity Summary**\n"
        references += f"- Total sources verified: {len(sources)}\n"
        references += f"- Technology choices validated: {sources_metadata['data_integrity'].get('technology_choices_validated', False)}\n"
        references += f"- Hallucination risk: {sources_metadata['data_integrity'].get('hallucination_risk', 'unknown')}\n"
        references += f"- Manual review recommended: {sources_metadata['data_integrity'].get('manual_review_recommended', True)}\n"
        
        return markdown + references
    
    def _validate_mermaid_syntax(self, markdown: str) -> bool:
        """Validate Mermaid diagram syntax in PRD."""
        
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', markdown, re.DOTALL)
        
        if not mermaid_blocks:
            return False
        
        for block in mermaid_blocks:
            # Check for valid architecture diagram types
            if not any(kw in block.lower() for kw in ["graph", "flowchart", "stateDiagram"]):
                return False
            
            # Check for connections/flows
            if not ("->" in block or "-->" in block):
                return False
        
        return True
    
    def _parse_sections(self, markdown: str) -> Dict:
        """Parse PRD markdown into structured sections."""
        
        sections = {}
        current_section = None
        content = []
        
        for line in markdown.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(content).strip()
                current_section = line.replace('## ', '').strip()
                content = []
            elif current_section:
                content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(content).strip()
        
        return sections


async def generate_prd(
    brd_dict: Dict,
    clarification_feedback: Optional[str] = None,
    run_count: int = 1
) -> Dict:
    """Generate technical PRD from approved BRD with web search and architecture validation."""
    skill = PESkill()
    return await skill.generate_prd(
        brd_dict=brd_dict,
        clarification_feedback=clarification_feedback,
        run_count=run_count
    )
