"""Authored visual summaries. Full explanations and supplied sources stay in the deck.

These are teaching redraws, not empirical findings or claims about real services.
The short labels are deliberately written per concept rather than truncated by code.
"""

STORIES = {
10: '''
X01|A working service can still be unsafe or untrustworthy.|Availability:Ready when needed;Reliability:Correct service;Safety:Avoid harm;Security:Resist attack;Resilience:Continue critical services|props
X02|Find the failure mechanism before choosing the fix.|Hardware:Physical fault;Software:Design fault;Operation:People and process|compare
X02A|Dependability spans the whole lifecycle, including operation and recovery.|Prevent + discover:Reduce faults;Tolerate + protect:Limit disruption and attack;Configure + recover:Control change and restore|flow
X03|The software is only one layer of the system.|Equipment:Physical operation;Software:Control decisions;People:Interpret and act;Organization:Rules and oversight|layers
R08|More copies help only against the failures they do not share.|Redundancy:Extra capacity;Diversity:Different solutions;Shared cause:Can defeat both|rd
X04|Spend on the failures whose consequences justify the extra assurance.|Higher assurance:More effort;Residual risk:Still explicit|p15
X05|A dependable process leaves evidence another person can inspect.|Specify:State obligations;Review:Find and resolve issues;Verify:Record the result|flow
R18|Short iterations still need traceable safety and assurance evidence.|Small change:Bound the scope;Review and test:Inspect the evidence;Controlled release:Keep the record|flow
X06|A proof establishes a property within a model and its assumptions.|Specification:Required property;Proof:Model satisfies it;Environment:Assumptions still matter|flow
X07|A fault can create an error; an error can become a visible failure.|Fault:Defect or cause;Error:Incorrect state;Failure:Service deviates|flow
''',
11: '''
X01|Manage faults before they become service failures.|Avoid:Prevent introduction;Detect:Find and remove;Tolerate:Limit the effect|flow
X02|A defect may stay dormant until a particular input activates it.|Fault:Present in the system;Activation:Operating condition;Failure:Observed deviation|flow
X03|Reliability is a claim about specified use, not every possible use.|Input mix:What users do;System:Processes requests;Output:Correct or failed|ch11_iomap
X04|Choose the metric, then state its denominator.|POFOD:Failures per demand;ROCOF:Failures per exposure;MTTF:Mean time to failure;Availability:Uptime / total time|metrics
X05|Availability becomes meaningful when you state the service and time window.|Window:30 days;Availability:99.9%;Downtime:43.2 minutes|flow
X06|Define the failure type before selecting a POFOD target and its evidence.|Transient failure:User can restore operation;Permanent failure:Manufacturer intervention;Evidence:Demands, failures and uncertainty|compare
X02A|Functional reliability requirements specify checks, recovery, redundancy and process obligations.|Checking:Find invalid states;Recovery:Restore operation;Redundancy:Tolerate faults;Process:Required development practices|compare
R09|Protection intervenes; self-monitoring detects disagreement.|Normal channel:Performs the work;Monitor:Checks the behavior;Protection:Acts on danger|ch11_selfmon
B01|Voting can mask an independent fault; common faults can defeat the vote.|Replicas:Produce results;Voter:Chooses an output;Shared error:May fool every version|ch11_tmr
R08|Trace both diversity and shared dependencies in the architecture.|Separate channels:Limit some failures;Diverse designs:Reduce shared faults;Common assumptions:Still need review|ch11_airbus
R18|Make invalid states and error paths explicit in the code.|Validate inputs:Check boundaries;Handle errors:Define recovery;Manage resources:Protect shared state|flow
X09|A reliability estimate needs failures, exposure and a representative test.|Operational profile:Select the mix;Execute tests:Observe failures;Estimate:Report scope and uncertainty|ch11_relmeasure
X10|A changed workload can invalidate an earlier reliability estimate.|Test mix:Ordinary requests;Production mix:Many retries;Action:Justify or retest|ch11_opprofile
''',
12: '''
X01|Safety asks whether the system can cause unacceptable harm.|Hazard:Potential for harm;Accident:Harm occurs;Control:Reduce the risk|flow
X02|Correctly implementing an unsafe requirement does not make a system safe.|Specification:Unsafe obligation;Implementation:Follows it correctly;System:Can still cause harm|flow
X02A|Separate the danger, the event and the consequence.|Hazard:Potential danger;Risk:Likelihood and consequence;Safety:Acceptable risk argument|compare
X03|Start with a hazard and trace it to a verifiable requirement.|Identify:What can harm?;Assess:How serious?;Analyze:How could it happen?;Reduce:What must change?|flow
X04|Risk acceptance needs an explicit criterion and a responsible decision.|Unacceptable:Reduce or avoid;Tolerable:Justify controls;Acceptable:Keep the evidence|ch12_risktri
X05|A fault tree describes logic; probability calculations need extra assumptions.|Top event:Harmful outcome;OR gate:Any branch sufficient;AND gate:Branches jointly needed|ch12_faulttree
X06|A safety requirement must identify the control and how to verify it.|Hazard:Excess dose;Control:Bound the dose;Verification:Exercise the boundary|flow
X09|Track the safety argument as requirements and implementations change.|Hazard record:Identified concern;Design control:Linked requirement;Verification:Versioned evidence|flow
R09|A hazard log is useful when each unresolved risk has an owner and next action.|Hazard:Describe it;Owner:Accountable reviewer;Status:Evidence and closure|flow
R18|Model checking explores the model, including states humans may overlook.|Model:States and transitions;Property:What must hold;Result:Proof or counterexample|ch12_modelcheck
D12|A clean analysis report does not establish complete system safety.|Code:What was analyzed;Rules:Defects sought;Limits:What remains unchecked|flow
B01|Connect the safety claim to evidence through an explicit argument.|Claim:What is safe?;Argument:Why does evidence support it?;Evidence:What was checked?|ch12_structarg
X10|An argument must cover the relevant paths and name its assumptions.|Path analysis:Inspect each branch;Safety condition:Show why it holds;Assumptions:State what remains external|ch12_safetyarg
''',
13: '''
X01|Security protects the conditions on which other dependability claims rely.|Confidentiality:Authorized disclosure;Integrity:Authorized changes;Availability:Authorized access|compare
X02|A control should interrupt a specific route from weakness to loss.|Asset:Patient record;Vulnerability:Weak credentials;Attack:Unauthorized access;Control:Enforce access rules|flow
X02A|Protection is needed in infrastructure, application and operation.|Infrastructure:Networks and platforms;Application:Software behavior;Operation:People and procedures|ch13_layers
X03|A policy becomes useful when it leads to a testable security obligation.|Asset:What matters?;Risk:What can go wrong?;Policy:What must be protected?|ch13_riskproc
X04|Risk assessment connects assets, threats, controls and remaining exposure.|Identify:Assets and threats;Assess:Exposure and feasibility;Control:Choose protections;Review:Residual risk|flow
X05|State who may perform which action on which resource.|Subject:Authenticated user;Action:Read or export;Object:Permitted records;Test:Reject unauthorized access|flow
X06|A misuse case makes the attacker's goal and your response explicit.|Attacker goal:Obtain another record;Attack path:Bypass a boundary;Mitigation:Enforce and test the boundary|ch13_misuse
R11|Reassess risk when the design changes where assets and trust are located.|Asset location:Where is the data?;Trust boundary:Who can reach it?;Control evidence:What checks access?|flow
R09|Use secure defaults, least privilege and several independent checks.|Default:Deny unless allowed;Privilege:Minimum needed;Validation:Check each boundary|flow
B01|A breach at one layer should encounter another effective protection.|Platform:Protect execution;Application:Enforce authorization;Data:Protect stored information|ch13_layered
X09|Treat external input as untrusted and make failure behavior deliberate.|Input:Validate meaning;Operation:Use safe interfaces;Failure:Reject and record safely|flow
R18|Combine different assurance methods; no single one covers every attack.|Review:Known weaknesses;Test:Attempt misuse;Analyze:Inspect code and behavior;Verify:Specified properties|compare
''',
14: '''
X01|Recovery matters only if the essential service becomes usable again.|Disruption:Something fails;Essential service:What must continue?;Recovery:Restore a bounded service|flow
X02|Recognize disruption, resist its effects, recover, then reinstate.|Recognize:Detect the disruption;Resist:Limit its effect;Recover:Restore essentials;Reinstate:Return to normal|ch14_resactivities
X02A|Plan for the loss of people, information and dependencies as well as servers.|Critical service:Define the minimum;Disruption:Choose a scenario;Rehearsal:Test the response|ch14_cyberplan
X03|Resilience depends on people knowing when and how to act.|Awareness:Recognize conditions;Authority:Make a decision;Coordination:Act across teams|ch14_orgresil
X04|Several defenses can fail together when their weaknesses align.|Layer one:Has limits;Layer two:Has limits;Shared weakness:Can cross every layer|ch14_swiss
X05|Maximum short-term efficiency may remove the capacity needed for recovery.|Efficiency:Less spare capacity;Resilience:Room to absorb disruption;Decision:Justify the trade-off|compare
D14|A rehearsal must test human work and data recovery, not just server restart.|Recognize:Interpret the situation;Act:Use an authorized fallback;Reconcile:Check restored records|flow
X06|Analyze essential services, intrusion scenarios and the recovery strategy.|Understand:System and mission;Identify:Critical assets;Analyze:Compromise scenarios;Decide:Survival strategy|ch14_survivability
R18|A live server is insufficient if staff cannot deliver the critical service.|Server:Running;Identity:Staff can sign in;Records:Available and usable;Service:Actually delivered|flow
B01|A resilient design needs a tested path from disruption to useful service.|Detect:Observe the failure;Switch:Use a controlled fallback;Recover:Verify restored operation|ch14_mentcare
R09|More data copies improve availability only with suitable access protection.|Replica:Another usable copy;Access control:Limit who can read;Reconciliation:Preserve correct records|flow
''',
15: '''
X01|Reuse can replace a function, component, application or whole system.|Function:Small abstraction;Component:Reusable service;Application:Existing product;System:Configured solution|compare
X02|Compare saved development effort with integration and lifecycle costs.|Benefit:Reuse tested work;Cost:Adapt and integrate;Long term:Support and change|compare
X02A|Select an approach by fit; the full fifteen-approach table remains in Details.|Code reuse:Libraries and patterns;Structure reuse:Frameworks and product lines;Product reuse:Configured or integrated systems|compare
D15|Choose reuse using schedule, lifetime, experience, criticality, domain and platform.|Fit:Functions and constraints;Variation:What can change?;Validation:Does this configuration work?|flow
X03|A library is called by your code; a framework calls your extension code.|Library:You control the calls;Framework:It controls the sequence|ch15_inversion
X04|A product line combines a common core with controlled variation.|Shared core:Family-wide features;Variation:Planned differences;Product instance:Selected configuration|ch15_basesystem
X05|Build a product instance by negotiating needs, selecting and validating a configuration.|Needs:State constraints;Configuration:Choose the variation;Validation:Check the actual instance|ch15_instance
X06|Adopting one product differs from integrating several independent products.|COTS solution:Configure one product;COTS integration:Connect several products;Both:Check non-functional fit|compare
R18|ERP combines business functions around shared information and configured processes.|Shared data:Common records;Business modules:Different functions;Configuration:Organizational rules|ch15_erparch
R09|A wrapper exposes a usable interface; it does not remove the product's limitations.|Existing product:Retains its behavior;Wrapper:Translates the interface;New system:Still must validate the contract|ch15_wrapping
''',
16: '''
X01|Components are composed through published interfaces and explicit dependencies.|Component:Encapsulated service;Provides:What it offers;Requires:What it needs|ch16_interfaces
X02A|A reusable component must be documented and deployable in a defined environment.|Standardized:Shared model;Independent:Explicit dependencies;Composable:Compatible interfaces;Deployable:Executable unit;Documented:Usable contract|compare
X03|Check what one component provides against what another requires.|Caller:Needs a service;Contract:Shared meaning;Provider:Offers the service|ch16_interfaces
X04|A component model defines rules; middleware supplies execution support.|Model:Interfaces and conventions;Component:Implements the rules;Middleware:Runs and connects components|ch16_modelelements
X05|Building a reusable component and building with components are different activities.|For reuse:Generalize and publish;Repository:Describe and manage;With reuse:Select and compose|ch16_cbseprocess
X06|Selection is followed by adaptation, composition and validation.|Discover:Find candidates;Adapt:Resolve mismatches;Compose:Connect services;Validate:Test the result|ch16_withreuse
R08|Previous success does not establish suitability in a new operating environment.|Old context:Known assumptions;New context:Different conditions;Evidence:Revalidate the assumptions|flow
B01|Composition can sequence operations, nest service use or combine interfaces.|Sequential:One then another;Hierarchical:One uses another;Additive:Combine offered services|ch16_composition
R09|An adapter must reconcile meaning as well as names and data types.|Input:30 minutes;Adapter:Validate and multiply by 60;Output:1800 seconds|ch16_adaptor
D16|Preconditions constrain the caller; postconditions constrain the result.|Before:Unused photo ID;Operation:addItem;After:Size = size@pre + 1|flow
D16B|Test accepted inputs, rejected inputs and the behavior of the composition.|Positive:Valid input succeeds;Negative:Invalid input is rejected;Integration:Components agree on meaning|compare
''',
17: '''
X01|Independent computers communicate, so partial failure is a normal design concern.|Client:May remain available;Network:May lose messages;Server:May execute independently|flow
X02|Review all six distributed-system design issues; improving one can constrain another.|Transparency + openness:Hide distribution and support integration;Scalability + security:Handle growth and protect access;Quality of service + failure management:Meet targets and handle partial failure|compare
X02A|A missing response leaves the caller uncertain about execution.|Request:Sent to server;Execution:May have completed;Response:Lost or delayed;Retry:May duplicate the effect|flow
X03|RPC resembles a call; messaging decouples interaction but still needs failure semantics.|RPC:Request and response;Messaging:Exchange explicit messages;Both:Handle loss and duplication|compare
X04|Middleware supplies common communication and coordination services.|Application:Domain behavior;Middleware:Communication support;Platform:Execution environment|ch17_middleware
X05|The four layers separate display, client-data handling, application processing and the database.|Presentation:Show information and interactions;Data handling:Check and manage client data;Application processing:Perform domain work;Database:Store and retrieve records|ch17_layered
X06|Compare five patterns against the workload and failure consequences.|Master–slave:Coordinate dedicated workers;Two-tier client-server:Clients and a server;Multi-tier client-server:Separate service tiers;Distributed component:Provide and use services;Peer-to-peer:Share distributed roles|compare
R09|Layers describe responsibilities; tiers describe deployment boundaries.|Logical layers:What the parts do;Physical tiers:Where they execute|compare
B01|The full five-pattern comparison belongs beside the specific workload.|Demand:Required interaction;Pattern:Organization of parts;Trade-off:Bottleneck and failure modes|flow
X07|A thin client relies more on the server; a fat client performs more local processing.|Thin client:More server work;Fat client:More local work;Choice:Deployment and failure trade-offs|compare
X09|Shared SaaS infrastructure still needs explicit tenant isolation.|Tenant A:Authorized data;Shared service:Enforced boundaries;Tenant B:Separate authorization|ch17_multitenant
X10|SaaS is a delivery model; SOA is an architectural style.|SaaS:How software is delivered;SOA:How services are organized;Can coexist:One does not imply the other|compare
''',
20: '''
X01|Constituent systems retain useful purposes and owners of their own.|System A:Independent owner;Shared capability:Depends on cooperation;System B:Independent purpose|compare
X02|Complexity comes from parts, relationships and independent change.|Technical:Components and interactions;Managerial:Different owners;Governance:Different rules and priorities|compare
X02A|Classify an SoS by its coordination and authority, not only its connections.|Directed:Central purpose and control;Collaborative:Voluntary coordination;Virtual:No central management|compare
X03|Correct parts do not guarantee a correct shared service.|Constituents:Pass local tests;Interactions:Introduce dependencies;Emergence:Creates system-level behavior|ch20_reality
X04|Engineering an SoS includes finding systems and negotiating cooperation.|Shared goal:What creates value?;Constituents:Who can contribute?;Agreement:Interfaces and authority;Evolution:Staged change|ch20_soseng
X05|Interfaces must carry shared meaning while owners retain control.|Provider:Publishes a contract;Interface:Data, version and access;Consumer:Interprets the same meaning|ch20_serviceiface
X06|Test the shared journey across owners, versions and operating conditions.|Local test:One constituent;Integration test:Cross-system behavior;Change test:Independent evolution|flow
X09|Design for useful operation despite incomplete participation and independent change.|Loose coupling:Limit dependencies;Bounded value:Work with partial participation;Evolution:Expect change|compare
X10|An architecture framework structures questions; it does not supply missing authority.|Architecture vision:Shared purpose;Design and migration:Planned relationships;Governance:Agreements and review|ch20_togaf
X08|Choose the interaction that the shared service actually requires.|Data feed:Publish observations;Container:Integrate services;Trading:Exchange between participants|compare
'''
}

CASES = {
10: ('The alarm is sounding. Can the plant continue?', 'A desalination upgrade is live. Pressure alarms recur; automatic failover runs. The cause remains uncertain.', 'Continue, restrict or revert?', ['Alarm', 'Failover', 'Evidence', 'Decision']),
11: ('The pump works in the test. What about tonight?', 'An insulin-pump update is operating in a different usage context. The release needs a measurable reliability claim.', 'Which measurement would support that claim?', ['Failures', 'Exposure', 'Usage profile', 'Requirement']),
12: ('The program followed its rules. A patient was harmed.', 'In this fictional case, a pump exceeds its dose limit and the expected audible alarm does not sound.', 'Which hazard-control link failed?', ['Hazard', 'Requirement', 'Control', 'Verification']),
13: ('A patient record has escaped the system.', 'A fictional Mentcare breach exposes a record. Identify the attack path before choosing the protection.', 'Which boundary should have stopped the access?', ['Asset', 'Attack path', 'Control', 'Test']),
14: ('The backup is running. The clinic still cannot work.', 'After a fictional ransomware incident, the backup starts but staff cannot access patient records.', 'Has the essential service recovered?', ['Disruption', 'Fallback', 'Usable service', 'Recovery']),
15: ('The purchased system does not fit the real workflow.', 'A fictional appointment product cannot support required waiting periods and linked bookings.', 'Configure, integrate or replace?', ['Needs', 'Reuse choice', 'Fit evidence', 'Decision']),
16: ('The interfaces match. The alert still fails.', 'A component reused in Mentcare carries assumptions from a different domain.', 'Which contract assumption must be tested?', ['Requires', 'Provides', 'Meaning', 'Test']),
17: ('The service crashes after receiving a request.', 'A fictional distributed Mentcare service loses a response during an urgent operation.', 'What may happen if the caller retries?', ['Request', 'Execution', 'Lost response', 'Retry']),
20: ('Several agencies connect. Who controls the outcome?', 'A fictional emergency-response service connects independently managed systems.', 'What can the shared service promise?', ['Independent owners', 'Shared interfaces', 'Joint evidence', 'Bounded decision'])
}

def attach(lecture):
    chapter=lecture['path']['chapter']
    story={}
    for line in STORIES[chapter].strip().splitlines():
        key,takeaway,nodes,visual=line.split('|')
        story[key]={'takeaway':takeaway,'nodes':[n.split(':',1) for n in nodes.split(';')],'visual':visual}
    headline,case,question,nodes=CASES[chapter]
    lecture['visualStory']={'units':story,'opening':{'headline':headline,'case':case,'question':question,'nodes':nodes},'version':'20260921-visual-v3'}
    return lecture
