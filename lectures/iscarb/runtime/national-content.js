/* Course-authored English crosswalk. Not official Jaheziah exam codes. */
window.ISCARB_NATIONAL = {
  "version": "20260928-national-en-v2",
  "chapters": {
    "10": {
      "knowledge": "Distinguish dependability properties",
      "skill": "Connect failures to their effects",
      "value": "Name the decision owner",
      "evidence": "Bounded claim + mechanism + evidence",
      "check": "Distinguish dependability, safety and security; explain how common causes limit redundancy and diversity.",
      "ai": "Critique an assistant’s recommendation for a water plant",
      "focus": "R08"
    },
    "11": {
      "knowledge": "Distinguish reliability and availability",
      "skill": "Calculate the right metric",
      "value": "State the limits of measurement",
      "evidence": "Metric + unit + operational profile",
      "check": "Choose POFOD, ROCOF, MTTF or AVAIL and explain why it fits the observed exposure.",
      "ai": "Examine a reliability claim about a learned component",
      "focus": "METRICS"
    },
    "12": {
      "knowledge": "Distinguish hazards and risk",
      "skill": "Trace a hazard to a requirement",
      "value": "Keep safety claims within the evidence",
      "evidence": "Hazard → requirement → verification",
      "check": "Read fault-tree gates; state independence assumptions and the limits of the safety argument.",
      "ai": "Test the limits of a safety-related recommendation",
      "focus": "X05"
    },
    "13": {
      "knowledge": "Distinguish assets, threats and vulnerabilities",
      "skill": "Design a misuse test",
      "value": "Protect data and access rights",
      "evidence": "Misuse + control + negative test",
      "check": "Connect policy to a testable requirement and state exactly what the test establishes.",
      "ai": "Critique an access decision involving an AI assistant",
      "focus": "X06"
    },
    "14": {
      "knowledge": "Distinguish recovery and restoration",
      "skill": "Plan service continuity",
      "value": "Name the emergency owner",
      "evidence": "Essential service + fallback + recovery",
      "check": "Preserve the essential service; explain fallback dependencies, activation authority and restoration risks.",
      "ai": "Simulate an assistant outage during a crisis",
      "focus": "X06"
    },
    "15": {
      "knowledge": "Distinguish approaches to reuse",
      "skill": "Compare fit and integration cost",
      "value": "Disclose supplier dependencies",
      "evidence": "Comparison + constraints + justified choice",
      "check": "Compare alternatives against requirements and lifecycle costs; explain when the fit claim no longer holds.",
      "ai": "Compare a hosted model with local operation",
      "focus": "IOC"
    },
    "16": {
      "knowledge": "Distinguish interfaces and semantic contracts",
      "skill": "Test conditions and compatibility",
      "value": "Verify before reusing",
      "evidence": "Contract + adapter + test case",
      "check": "Distinguish signature compatibility from semantic compatibility; test a precondition, a postcondition and a composition failure.",
      "ai": "Specify a contract for an AI component",
      "focus": "B01"
    },
    "17": {
      "knowledge": "Explain communication uncertainty",
      "skill": "Trace failures and retries",
      "value": "Keep unconfirmed success explicit",
      "evidence": "Trace + owner + failure response",
      "check": "Distinguish a lost response from failed execution; justify the architecture and limits of retrying a request.",
      "ai": "Analyze retries to an AI service",
      "focus": "X02A"
    },
    "20": {
      "knowledge": "Explain system independence",
      "skill": "Test interactions across owners",
      "value": "Respect authority boundaries",
      "evidence": "Interface + owner + joint test",
      "check": "Connect operational and managerial independence to interfaces, incremental deployment and testing across owners.",
      "ai": "Critique an AI-generated flow across organizations",
      "focus": "X05"
    }
  },
  "principles": [
    "Learning first",
    "Clear educational value",
    "Human-centered design",
    "Responsible design",
    "Evidence-based improvement"
  ],
  "stages": [
    "Define",
    "Design",
    "Enhance",
    "Assign roles",
    "Evaluate",
    "Verify & improve"
  ]
};
