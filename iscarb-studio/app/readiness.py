from __future__ import annotations

import json

# Source: Education and Training Evaluation Commission (ETEC),
# Academic Standards for Information Technology Programs, 2025, Version 2.0.
# This profile is deliberately compact: it is an alignment authority, NOT a
# replacement for the weekly technical lecture source.
ETEC_IT_READINESS = {
    "authority": "Education and Training Evaluation Commission (ETEC)",
    "standard": "Academic Standards for Information Technology Programs",
    "year": 2025,
    "version": "2.0",
    "scope": (
        "Minimum required knowledge, skills, and values for Saudi bachelor-level "
        "Information Technology programs; the document also supports standardized "
        "test creation and accreditation."
    ),
    "standardized_test_rule": (
        "Essential Knowledge Units (EKUs) are explicitly excluded from standardized tests. "
        "Readiness alignment in ISCARB therefore targets relevant Computing GKUs/SKUs/SLOs, "
        "not EKUs."
    ),
    "klo": {
        "KLO1": "Specialist Knowledge for Solving Computing Problems: apply computing fundamentals, specialization knowledge, and appropriate domain knowledge to conceptualize models for defined problems and requirements and demonstrate in-depth professional knowledge.",
        "KLO2": "Problem Analysis: identify, formulate, research, and analyze complex computing problems; conduct investigation through experiments, data analysis/interpretation, and synthesis to reach valid substantiated conclusions with holistic considerations.",
        "KLO3": "Design/Development of Solutions: design solutions, systems, components, or processes for complex computing problems with appropriate consideration of health and safety, privacy and security, cybersecurity, lifecycle cost, sustainability, culture, society, and environment.",
        "KLO4": "Modern Tool Usage: create, select, adapt, and apply appropriate techniques, resources, and modern computing tools, including simulation, prediction, and modelling, while recognizing their limitations.",
        "KLO5": "Individual and Team Work: participate effectively as an individual, member, or leader in diverse and inclusive multidisciplinary, face-to-face, remote, and distributed teams.",
        "KLO6": "Project Management and Finance: apply IT management principles with consideration of market needs and budget to manage projects in multidisciplinary environments.",
        "KLO7": "Communication: communicate effectively about complex computing activities through reports, design documentation, and presentations while considering cultural, language, and learning differences.",
        "KLO8": "Computing Professionalism and Society: analyze impacts of professional computing practices and solutions on society, economy, privacy/security, cybersecurity, health/safety, legal frameworks, governance, entrepreneurship, and environment.",
        "KLO9": "Ethics: apply ethical principles and professional norms, accept responsibilities, incorporate diversity and inclusion, and comply with relevant local and international laws.",
        "KLO10": "Life-long Learning: independently acquire new knowledge, adapt to emerging computing technologies, and exercise critical thinking in the broad context of technological advancement.",
    },
    "gku_weights": {
        "GKU1 User Experience Design": "10%",
        "GKU2 Global Professional Practice": "10%",
        "GKU3 Cybersecurity Principles": "10%",
        "GKU4 Networking": "10%",
        "GKU5 Platform Technologies": "10%",
        "GKU6 Information Management": "15%",
        "GKU7 System Paradigms": "10%",
        "GKU8 Software Fundamentals": "15%",
        "GKU9 Web and Mobile Systems": "10%",
    },
    "skus": {
        "SKU2.2": {
            "gku": "GKU2 Global Professional Practice",
            "name": "Ethical, legal, and privacy issues",
            "weight": "2.5% of GKU distribution table",
            "source_pages": [18],
            "topics": ["Ethical issues in IT", "Legal issues in IT", "Privacy issues in IT", "Intellectual property issues in IT"],
            "slos": {
                "SLO2.2.1": "Evaluate the role of legal, ethical, and privacy issues within IT as it relates to organizations.",
                "SLO2.2.2": "Model a computer use policy that includes privacy, legal, and ethical considerations for all employees.",
                "SLO2.2.3": "Apply the principles of intellectual property within IT contexts.",
                "SLO2.2.4": "Describe several transnational issues concerning intellectual property.",
            },
        },
        "SKU3.1": {
            "gku": "GKU3 Cybersecurity Principles",
            "name": "Cyber attacks, vulnerabilities, threats, risk, and detection",
            "weight": "5% of GKU distribution table",
            "source_pages": [19, 20],
            "topics": [
                "Types of cyber attacks and vulnerabilities",
                "Threats and risks in computing environments",
                "Methods and tools for detecting and mitigating attacks",
                "Risk management and prevention approaches across systems, networks, and devices",
            ],
            "slos": {
                "SLO3.1.1": "Explain common types of cyber attacks, vulnerabilities, and their corresponding detection methods.",
                "SLO3.1.2": "Compare vulnerabilities, threats, and risk, as well as how they interrelate.",
                "SLO3.1.3": "Apply risk management frameworks and use appropriate tools to identify vulnerabilities and threats.",
                "SLO3.1.4": "Analyze data from detection systems and propose mitigation strategies.",
                "SLO3.1.5": "Recognize specific vulnerabilities, threats, and risks associated with diverse platforms such as networks, cloud computing, desktops, and mobile devices.",
            },
        },
        "SKU3.2": {
            "gku": "GKU3 Cybersecurity Principles",
            "name": "Cryptography overview",
            "weight": "5% of GKU distribution table",
            "source_pages": [21],
            "topics": [
                "Public-key, symmetric-key, hash functions, and digital signatures",
                "Authentication and data security",
                "Privacy and encryption at block, file, and application levels",
            ],
            "slos": {
                "SLO3.2.1": "Identify various types of cryptography.",
                "SLO3.2.2": "Compare cryptography algorithms to assess strengths, weaknesses, and practical applications.",
                "SLO3.2.3": "Explain block-level, file-level, and application-level encryption for encrypted storage.",
            },
        },
        "SKU7.1": {
            "gku": "GKU7 System Paradigms",
            "name": "Requirements engineering",
            "weight": "5% of GKU distribution table",
            "source_pages": [28],
            "topics": ["Fundamentals of requirements engineering", "Modeling techniques", "Functional vs non-functional requirements", "Creating and analyzing use cases"],
            "slos": {
                "SLO7.1.1": "Apply fundamentals of basic requirements engineering, including various modeling techniques.",
                "SLO7.1.2": "Contrast functional and non-functional requirements.",
                "SLO7.1.3": "Design detailed use cases, illustrating structure, event flows, and relationships between functional requirements and use case scenarios.",
            },
        },
        "SKU7.2": {
            "gku": "GKU7 System Paradigms",
            "name": "Testing and quality assurance",
            "weight": "5% of GKU distribution table",
            "source_pages": [29],
            "topics": ["System testing standards", "User acceptance testing"],
            "slos": {
                "SLO7.2.1": "Describe different ways for current testing standards.",
                "SLO7.2.2": "Illustrate different ways to execute and evaluate an acceptance test.",
            },
        },
        "SKU8.1": {
            "gku": "GKU8 Software Fundamentals",
            "name": "Problem solving and program development",
            "weight": "9.5% of GKU distribution table",
            "source_pages": [30, 31],
            "topics": ["Abstraction, decomposition and modeling", "Iterative program development", "Program documentation", "Programming tools", "Version control, project hosting and deployment"],
            "slos": {
                "SLO8.1.1": "Use abstraction and decomposition strategies to design a solution to a complex IT problem.",
                "SLO8.1.2": "Develop a program using an iterative process to solve specified problems effectively.",
                "SLO8.1.3": "Create comprehensive program documentation and integrate user feedback to enhance program functionality.",
                "SLO8.1.4": "Analyze a program's design and implementation by assessing coding style, correctness, and expected behavior on specific inputs, and provide feedback on intended functionality.",
                "SLO8.1.5": "Design a program using tools relevant to current industry practices: version control, project hosting, and deployment services.",
            },
        },
        "SKU8.2": {
            "gku": "GKU8 Software Fundamentals",
            "name": "Fundamentals of data structures and algorithms",
            "weight": "5.5% of GKU distribution table",
            "source_pages": [32],
            "topics": ["Fundamental data structures", "Algorithmic program development", "Abstract data types", "Recurrence relations", "Formal reasoning on algorithm efficiency"],
            "slos": {
                "SLO8.2.1": "Decide on appropriate data structures for modeling a given problem.",
                "SLO8.2.2": "Create algorithms to solve a computational problem.",
                "SLO8.2.3": "Apply mathematical concepts and abstract data types to develop and analyze programming solutions.",
                "SLO8.2.4": "Utilize recurrence relations and formal reasoning to evaluate and ensure algorithm efficiency and correctness.",
            },
        },
        "SKU9.1": {
            "gku": "GKU9 Web and Mobile Systems",
            "name": "Web and mobile systems concepts and technologies",
            "weight": "10% of GKU distribution table",
            "source_pages": [33, 34],
            "topics": ["Web and mobile application technologies", "Data validation", "Client vs server-side development", "Cookies", "Server-side database connectivity", "JavaScript"],
            "slos": {
                "SLO9.1.1": "Develop a web or mobile application that uses industry-standard technologies.",
                "SLO9.1.2": "Develop a web or mobile application that validates data inputs on client and server sides as appropriate, uses cookies, and uses JavaScript.",
                "SLO9.1.3": "Develop a web or mobile application that reads or modifies data in a server-side database.",
                "SLO9.1.4": "Write, debug, and test a script that includes selection, repetition, and parameter passing.",
                "SLO9.1.5": "Use scripting languages for web scripting, server-side scripting, and operating-system scripting.",
            },
        },
    },
    "alignment_rules": [
        "Select only KLO/SKU/SLO targets that the weekly technical source genuinely supports.",
        "Never add cryptography, testing, programming, or any other standard topic merely to claim readiness alignment if the weekly source does not teach it.",
        "Program-level KLOs may be aligned through authentic weekly evidence, but the rationale must identify the learner performance that supports the alignment.",
        "A Gulf readiness webpage may be used as orientation only; this ETEC standard is the authoritative competency reference embedded in ISCARB for IT readiness.",
        "Readiness evidence must be demonstration-based: analysis, design, test, artifact, critique, or defended engineering decision rather than self-report or policy agreement.",
    ],
}

READINESS_CONTEXT = json.dumps(ETEC_IT_READINESS, ensure_ascii=False, indent=2)
