/* iSCARB story series v3 · "Layan's first year".
 * One fictional junior engineer (the student's seat) and her mentor carry the course; each chapter is
 * an episode with its own client, deadline and stakes. Every episode is built on that chapter's approved
 * fictional case: the scenes restate the case, the five acts follow the five roadmap branches in order,
 * and the twist is the changed constraint the lecture already reveals at station 3. Nothing here is
 * assessed content, and no scene settles the decision for the student.
 * People and organisations are fictional; any resemblance to real ones is coincidental.
 */
window.ISCARB_STORY = {
 series: 'Layan’s first year',
 // Rolled out from Chapter 12 (Assignment 3) on. Chapters 10 and 11 were already taught in the previous
 // design and stay that way; their pilot episodes are kept here, inactive, for a later offering.
 firstChapter: 12,
 // The course principle every episode shows: Layan practises with AI; what she signs is her own judgment.
 principle: 'AI is the practice layer. Your engineering judgment is what we assess.',
 lead: {name: 'Layan', role: 'Junior software engineer at a Jeddah engineering consultancy · your seat in the story'},
 mentor: {name: 'Khalid', role: 'Senior engineer · her mentor · always asks “what is your evidence?”'},
 chapters: {
  10: {
   practice: 'Layan asks an AI chat to play devil’s advocate on her alarm analysis. It sharpens her questions. It does not get a vote on whether the plant keeps running.',
   episode: 'Pilot A · The alarm at 02:10',
   setting: 'Night shift at a coastal desalination plant that supplies a city’s drinking water. Layan is on her first on-call rotation for the control-system upgrade.',
   client: {name: 'Huda', role: 'Plant shift supervisor · must decide whether the plant keeps running'},
   clock: 'Morning demand peak: 05:00',
   coldOpen: '02:10. The pressure alarm sounds for the third time tonight, and the system fails over on its own. On the screen, the new AI assistant says “likely sensor fault, 0.91.” Huda turns to Layan: “Can we keep running?”',
   stakes: 'Keep running through a real excursion and the city may wake up without water. Stop for a false alarm and the plant goes dark at peak demand for nothing.',
   gut: {q: 'Right now, with what you know, what do you tell Huda?', options: ['Keep running: the AI says sensor fault', 'Shut down: an alarm is an alarm', 'Neither yet: I need different evidence first']},
   acts: [
    'Huda wants one word: “safe?” Layan realises the alarms threaten more than one property at once, and each needs its own answer.',
    'Layan pulls the log: three alarms, one failover. Khalid, on the phone: “Fault, error or failure? Each one needs different evidence.”',
    'The upgrade spec promises “redundant pressure sensing.” Two readings sit side by side on the screen. Layan asks: are they really two paths?',
    'Huda asks for the decision in writing. Khalid: “Which process evidence would let you sign it?”',
    'The vendor emails a verified model of the failover logic. Layan wonders what that proof says about tonight’s transmitter.'
   ],
   twist: '03:30. Layan opens the vendor’s integration notes. The two “separate” readings share one transmitter and one power supply, and the AI detector scores the signal from that same transmitter.',
   epilogue: '05:00 arrives. Whatever Layan advised, Khalid’s first question in the morning review is the one you will face too: what did you claim, where does the claim stop, and what evidence would another engineer accept?'
  },
  11: {
   practice: 'Layan has an AI tutor quiz her on POFOD and ROCOF before the board meets. The release scope she recommends, and the evidence behind it, are hers.',
   episode: 'Pilot B · Release on Thursday',
   setting: 'A university is about to release a new communications gateway that also relays every student’s and staff member’s email. Layan’s team ran the pilot.',
   client: {name: 'Nouf', role: 'IT services director · promised the deans “99.99%”'},
   clock: 'Release board: Thursday 10:00',
   coldOpen: 'The dashboard has been green all pilot. Nouf wants to release on Thursday. Then Layan rereads the vendor slide, “98% accurate,” and the pilot log: the phishing filter missed 10 of the 50 phishing emails it saw.',
   stakes: 'Release too widely and phishing reaches every inbox while the 99.99% promise breaks in public. Hold without a reason and a service the deans are waiting for slips a whole term.',
   gut: {q: 'Thursday’s call: what do you recommend?', options: ['Release: it was available all pilot', 'Restrict: release to a limited scope', 'Hold: the evidence is not there yet']},
   acts: [
    '“It never went down,” says Nouf. Layan writes two words on the whiteboard: ready, and correct.',
    'Twenty failed demands in 10,000. Two outages in 1,000 hours. Layan must choose the metric, and the denominator, that the release claim actually needs.',
    'Nouf’s fix: “Add a second identical server.” Khalid asks which failure that would stop.',
    'Layan opens the code path that handles malformed messages. What prevents, contains or recovers from a fault there?',
    'The pilot used 10% external traffic. Layan goes to find out what the real mix will be after release.'
   ],
   twist: 'Wednesday evening, admissions confirms that after release, external traffic will be 60%, not 10%. No test used that mix, and the classifier was trained mostly on internal messages.',
   epilogue: 'Thursday 10:00. The board will ask Layan for one sentence: which scope, which metric, which evidence. Write yours before you leave the room.'
  },
  12: {
   lab: {"question": "Assignment 3’s loading-bay barrier: will it close when the camera has no usable image?", "cases": [{"name": "zone occupied", "frames": ["empty", "occupied"], "expectedAction": "hold"}, {"name": "zone clear", "frames": ["empty"], "expectedAction": "close"}, {"name": "camera covered", "frames": ["occupied", "missing"], "expectedAction": "hold"}]},
   practice: 'Layan asks an AI chat to play Tariq and argue for Monday. It helps her rehearse the conversation. The hazard analysis and the safety claim she signs are her own.',
   episode: 'Episode 1 · Every command within limits',
   setting: 'A plant is about to switch on a repeated-command mode for a controller whose safety argument Layan’s team prepared last year.',
   client: {name: 'Tariq', role: 'Operations manager · measured on throughput'},
   clock: 'New mode goes live: Monday, first shift',
   coldOpen: 'Tariq is delighted. The AI assistant’s command sequences raise throughput, and every single command passed the limiter. Operators now accept the sequences without editing them. Layan opens the safety case. It argues about one command at a time.',
   stakes: 'Approve without analysis and the floor runs on an actuation nobody has modelled. Block without evidence and a real gain is lost for a reason no one can inspect.',
   gut: {q: 'Can the new mode go live on Monday?', options: ['Yes: every command passed its check', 'No: switch the AI assistant off', 'Not until the safety argument covers repeated commands']},
   acts: [
    'Tariq: “The software meets its specification. How can it be unsafe?” Layan has to answer that first.',
    'Layan sketches the line on a whiteboard: what happens when many small commands add up, and how bad could it be?',
    'Khalid wants a requirement, not a worry: exactly what must the controller never allow?',
    'The test report checks one command at a time. Layan lists the evidence that would show the protection works.',
    'The safety case is due for sign-off. Does its argument even reach the new mode, or loss of sensing?'
   ],
   twist: 'Friday 16:00. A pilot trace: in repeated mode, the cumulative value went past the modelled limit while every individual command stayed within its bound. The sequences came from the AI assistant, which had found that many small commands raise throughput.',
   epilogue: 'Monday’s first shift is waiting. Khalid will sign only a claim with a stated boundary and the evidence behind it. What exactly would your safety claim cover, and what would it not?'
  },
  13: {
   lab: {"question": "Assignment 4’s portal: does hiding a link stop a direct request?", "cases": [{"name": "own project, direct request", "actor": "student:ali", "object": "project:ali@g1", "path": "api", "expected": "allow"}, {"name": "another student’s project, direct request", "actor": "student:sara", "object": "project:ali@g1", "path": "api", "expected": "deny"}, {"name": "staff, other group, via the interface", "actor": "staff:g2", "object": "project:ali@g1", "path": "ui", "expected": "deny"}]},
   practice: 'Layan uses an AI assistant to brainstorm misuse cases. It suggests ten. She chooses the one worth a negative test and writes the claim Khalid will sign.',
   episode: 'Episode 2 · The record that crossed the line',
   setting: 'A Jeddah startup sells a team-documents application to three client organisations. Next week it switches on an AI assistant that answers questions about each team’s files.',
   client: {name: 'Majed', role: 'Product owner · wants the assistant live on Sunday'},
   clock: 'Release sign-off: Sunday 09:00',
   coldOpen: 'Thursday 16:40. Every test is green, and every test logs in as the document’s owner. Layan types another team’s document ID into the address bar. The interface hides the link. Does the server refuse?',
   stakes: 'Ship it wrong and one client reads another client’s files: the startup loses all three. Hold it without evidence and the assistant pilot users loved misses its launch.',
   gut: {q: 'Sunday 09:00: can it ship?', options: ['Ship: the interface hides other teams’ links', 'Ship: the assistant is told to answer only from your team', 'Hold until a test shows the server refuses']},
   acts: [
    'Majed: “Nobody can even see other teams’ links, so where is the risk?” Layan starts by naming what is actually at stake.',
    'Who decides how much cross-team risk is acceptable: Majed, Khalid or the clients? Layan finds that the policy is silent.',
    'Khalid, who signs security releases, wants a requirement he could test, not “the system should be secure.”',
    'Layan traces where authorization really happens: in the interface, the API or the data layer.',
    'Time to write the negative test, and to say honestly what it does not cover.'
   ],
   twist: 'Saturday night, Layan reads the assistant’s integration notes. It never calls the API she tested. It reads documents through its own service account, one that can open every team’s files, and relies on an instruction to answer only from the asker’s team.',
   epilogue: 'Sunday 09:00. Khalid signs only what is tested. Layan’s note has three lines: claim, boundary, evidence. What would yours say?'
  },
  14: {
   lab: {"question": "Assignment 5’s transport desk: what can staff see during an outage?", "cases": [{"name": "change made during the outage", "events": ["change:p1", "refresh", "outage", "change:p1", "lookup:p1", "recover", "lookup:p1"], "expectedLookups": ["current", "current"], "expectedLost": 0}, {"name": "change made after the 06:00 refresh", "events": ["refresh", "change:p2", "outage", "lookup:p2"], "expectedLookups": ["missing"], "expectedLost": 0}]},
   practice: 'Layan rehearses the four Rs with an AI tutor during a quiet hour. When Amal asks “are we recovered?”, the answer and its evidence must be Layan’s.',
   episode: 'Episode 3 · 02:00, and nobody can sign in',
   setting: 'A public service’s records system after a cyber incident. The incident is contained. Khalid, the only trained recovery specialist, is off shift and not answering. Layan is on call.',
   client: {name: 'Amal', role: 'Service manager · must tell the public when counters reopen'},
   clock: 'Public counters open: 08:00',
   coldOpen: '02:00. The backup server is running, yet no one can complete a single transaction because the sign-in service is down. Khalid is unreachable. The organisation’s AI recovery assistant offers confident, step-by-step instructions. It has never been used in a rehearsal.',
   stakes: 'Declare recovery too early and counters open at 08:00 with staff still locked out. Follow untested steps and a second outage lands on top of the first.',
   gut: {q: 'Amal asks: “Are we recovered?” What do you say?', options: ['Yes: the backup server is running', 'Partly: something critical is still missing', 'Let the AI assistant decide and follow its steps']},
   acts: [
    'The servers are up, the service is not. Layan has to name what “critical service” means for the people at the counter.',
    'Amal wants a status update. Layan places the night on the four Rs: recognition, resistance, recovery, reinstatement.',
    'Everything waits on one sign-in service. Layan asks what else depends on it.',
    'The runbook assumes Khalid. Layan and two operators must decide what people can do when the procedure runs out.',
    'Before 08:00, Layan must show what restores usable service, not just running servers, and how she would know.'
   ],
   twist: '04:20. The alternate data copy comes up, but it signs in through the same identity service that is down. So does the AI recovery assistant, and its instructions assume the primary copy anyway.',
   epilogue: '08:00. Amal will announce something to the public. Khalid, back in the morning, will ask Layan which part of the service was restored, which was not, and who knew.'
  },
  15: {
   lab: {"question": "Assignment 6’s two options: which needs do the facts actually settle?", "cases": [{"name": "A has recurring bookings", "option": "A", "requirement": "recurring", "expected": "met"}, {"name": "B has recurring bookings", "option": "B", "requirement": "recurring", "expected": "gap"}, {"name": "A supported for three years", "option": "A", "requirement": "support-3-years", "expected": "gap"}, {"name": "A’s export is complete", "option": "A", "requirement": "export-api", "expected": "unknown"}]},
   practice: 'Layan asks an AI to summarise the supplier’s roadmap. Useful practice, but the reuse route, and what would change her mind, she must defend herself.',
   episode: 'Episode 4 · Buy, bend or build',
   setting: 'A clinic group bought an appointment product to replace its old booking system. Layan’s team must make it work for the clinics.',
   client: {name: 'Dr. Sara', role: 'Clinic operations lead · knows the real workflow'},
   clock: 'Contract decision: end of the month',
   coldOpen: 'Ordinary bookings work well. Then Dr. Sara shows Layan what the clinics do every day: follow-ups that must wait a set period, linked to the first visit. The product has no such thing. The supplier says “configure it.” The team also wants a hosted language model to draft replies; it handled a ten-request demo perfectly.',
   stakes: 'Commit to the wrong route and the clinics live with a mismatched workflow for years. Replace too fast and months of purchased software and data migration are thrown away.',
   gut: {q: 'First instinct for the clinic group?', options: ['Configure the product: the supplier says it can', 'Integrate the language model to fill the gaps', 'Not yet: test the full workflow before choosing']},
   acts: [
    'Layan lists what could be reused: a whole product, an application, a component, or just an idea.',
    'Khalid hands her the planning factors: schedule, lifetime, team, criticality, domain, platform. Does the product still fit?',
    'A colleague suggests a framework instead. Layan asks whether it gives structure without forcing the wrong workflow.',
    'Could a product line or configuration handle waiting periods and linked appointments?',
    'Configure, integrate, wrap or replace: Layan has to choose, and to show what evidence decides.'
   ],
   twist: 'Week three. The supplier announces it will change a required interface and stop supporting the earlier version long before the planned lifetime ends. The same week, the language-model version the team tested is scheduled for retirement; its replacement answers the same prompts differently.',
   epilogue: 'The contract decision is due. Dr. Sara does not need a perfect product; she needs to know which route survives the next five years, and what would make Layan change her mind.'
  },
  16: {
   lab: {"question": "Assignment 7’s adapter: what does “30 minutes” become inside the component?", "cases": [{"name": "normal booking", "durationMinutes": 30, "expectedStatus": "accepted", "expectedSeconds": 1800}, {"name": "upper boundary", "durationMinutes": 120, "expectedStatus": "accepted", "expectedSeconds": 7200}, {"name": "zero length", "durationMinutes": 0, "expectedStatus": "rejected", "expectedSeconds": null}]},
   practice: 'Layan has an AI generate test values for the adapter. She still decides which boundaries matter and writes the contract Rakan relies on.',
   episode: 'Episode 5 · Ninety-five degrees',
   setting: 'A city operations team is composing a heat-alert service from reusable parts: a sensor data component and a vendor’s AI forecasting component. Layan is the integrator.',
   client: {name: 'Rakan', role: 'Operations lead · issues public heat alerts'},
   clock: 'Heat-alert season starts next week',
   coldOpen: 'The interfaces connected the first time: number in, number out. The readings look plausible. Nobody has written down what the number means, and the forecaster’s documentation just says “temperature,” no unit.',
   stakes: 'Compose on a hidden assumption and the city issues confident, wrong alerts. Block the composition without a contract and the season starts with no service at all.',
   gut: {q: 'The interfaces match. Can Layan compose them?', options: ['Yes: the types match and values look normal', 'Yes: the AI will cope with odd values', 'Not until the meaning is written in the contract']},
   acts: [
    'Layan opens the provided and required interfaces side by side. Which one should state what the temperature means?',
    'The component model and its middleware connect everything. Do they define the unit, or just pass the number?',
    'Adapt the component, or change the requirement? Rakan cares about alerts, not architecture.',
    'If a conversion is needed, where in the composition should the adapter sit?',
    'Khalid asks for the contract, and for the test that would fail on a wrong unit or an invalid value.'
   ],
   twist: 'The provider’s updated documentation arrives: the values are Fahrenheit. 95 was never Celsius. The forecaster, trained on Celsius, accepted every value without error and returned confident, wrong forecasts.',
   epilogue: 'Rakan asks Layan one question before the season opens: “What stops this happening with the next component?” Her answer has to be a contract and a test, not a promise.'
  },
  17: {
   lab: {"question": "Assignment 8’s booking service: what happens when the reply is lost and the service restarts?", "cases": [{"name": "restart, same request identity", "events": ["send:a", "lose-response", "restart", "retry:a"], "expectedReservations": 1}, {"name": "retry with a new identity", "events": ["send:b", "lose-response", "retry:c"], "expectedReservations": 2}]},
   practice: 'Layan asks an AI to explain idempotency keys three different ways until it clicks. The retry design she commits to before 20:00 is her judgment.',
   episode: 'Episode 6 · Did it go through?',
   setting: 'A national events app is preparing for a big ticket sale. Layan works on the backend service that accepts each booking and sends the confirmation.',
   client: {name: 'Hessa', role: 'Customer support lead · her team answers the angry calls'},
   clock: 'Sale opens: 20:00 tonight',
   coldOpen: 'A user taps Confirm. The spinner turns, then the request times out. The app offers “Try again.” Did the first booking happen? The trace stops before the answer. Meanwhile, a hosted AI service drafts and sends every confirmation message.',
   stakes: 'Retry blindly and customers are charged or messaged twice at 20:00, by the thousand. Never retry and real bookings are silently lost.',
   gut: {q: 'The request timed out. Is it safe to retry?', options: ['Yes: a timeout means it failed', 'No: never retry', 'Only if a retry cannot do it twice']},
   acts: [
    'Hessa: “It timed out, so it failed, right?” Layan starts with what a timeout does and does not tell you.',
    'Layan compares the two ways the client and service talk: a remote call, or a message.',
    'Which layer owns the retry, the state and what the user sees: the app, the service or the database?',
    'Khalid asks which architecture would contain a duplicate or uncertain operation.',
    'Part of the system is someone else’s hosted service. Layan asks what evidence that ownership leaves her.'
   ],
   twist: 'A later trace arrives. The original booking committed before its reply was lost. The retry ran it again, and called the AI service again, which drafted a different confirmation. The customer received both.',
   epilogue: '20:00 is coming. Hessa needs to know what happens on a retry, and how support will tell a duplicate from a real second booking. What would Layan’s design guarantee, and what would it only detect?'
  },
  20: {
   lab: {"question": "Assignment 9’s dashboard: what should a slow or missing feed look like?", "cases": [{"name": "security, updated a minute ago", "feed": "security", "minutesSinceUpdate": 1, "available": true, "expectedDisplay": "live"}, {"name": "transport, 12 minutes old", "feed": "transport", "minutesSinceUpdate": 12, "available": true, "expectedDisplay": "stale"}, {"name": "facilities, feed down", "feed": "facilities", "minutesSinceUpdate": 3, "available": false, "expectedDisplay": "unavailable"}]},
   practice: 'Layan uses an AI chat to role-play the three agency owners. It is rehearsal. The bounded promise Faisal reads aloud is Layan’s, with her name on it.',
   episode: 'Episode 7 · Whose dashboard is it?',
   setting: 'A multi-agency incident dashboard combines data feeds from agencies Layan’s team does not control. Officials will rely on it.',
   client: {name: 'Faisal', role: 'Coordinator · briefs officials every morning'},
   clock: 'Officials’ briefing: tomorrow 07:30',
   coldOpen: 'The dashboard looks complete. Faisal wants to call it “real-time” in tomorrow’s briefing. Layan knows it can validate and display each feed, but it cannot tell any agency when to update, and one agency now produces its feed with an AI model nobody outside can inspect.',
   stakes: 'Promise too much and officials act on stale or reclassified data they think is live. Promise nothing and a useful shared picture goes unused.',
   gut: {q: 'Can the dashboard promise “real-time and complete”?', options: ['Yes: every feed is connected and valid', 'Yes, once each agency signs an agreement', 'Only a bounded promise the dashboard can check itself']},
   acts: [
    'Layan lists who owns what. Every agency runs its own system, for its own reasons.',
    'Faisal: “We are the principal system, so we are in charge.” Layan checks what authority the dashboard really has over each feed.',
    'Every feed passes its own checks. Layan explains why that still does not guarantee the shared picture.',
    'The owners must coordinate interfaces, staged changes and cross-system tests, without anyone being the boss.',
    'Khalid asks for an architecture that keeps the dashboard useful when one feed slows or changes.'
   ],
   twist: 'One agency quietly moves to a slower update schedule. Same format, so validation still passes. It also switched AI model versions: the feed’s shape is unchanged, but incidents are now classified differently.',
   epilogue: '07:30. Faisal will read Layan’s sentence aloud to officials. What can the dashboard honestly promise, and what must it show when a feed it does not control changes?'
  }
 }
};

/* Real-case anchors and the two roles of AI (revision 20261004-realcase).
   Every chapter gets one documented real incident that shows the same engineering pattern as its episode.
   Chapter 12 is told on an aircraft, after the 737 MAX MCAS accidents. */
(function (S) {
  if (!S || !S.chapters) return;
  S.desk = [
    'Ask it to play the reviewer and attack your argument.',
    'Ask it for test cases, then decide yourself which ones matter.',
    'Ask it the two-minute check questions and answer aloud.'
  ];
  const R = {
    12: {
      setting: 'An aircraft maker is adding an automatic trim function to a new airliner. The flight-control computer limits each nose-down trim command to a set maximum. Layan’s team wrote the safety argument last year.',
      client: {name: 'Tariq', role: 'Programme manager · measured on the certification date'},
      clock: 'Certification review: Monday, 09:00',
      coldOpen: 'Tariq is delighted. A new AI assistant proposes trim sequences that cut fuel burn, and every single command passed the limiter in the simulator. Test crews now accept its sequences without editing them. Layan opens the safety case. It argues about one command at a time.',
      stakes: 'Certify without analysis and the jet flies on trim authority nobody has modelled. Block without evidence and a real fuel saving is lost for a reason no one can inspect.',
      gut: {q: 'Can the new trim mode be certified on Monday?', options: ['Yes: every command passed its check', 'No: switch the AI assistant off', 'Not until the safety argument covers repeated commands']},
      acts: [
        'Tariq: “The software meets its specification. How can it be unsafe?” Layan has to answer that first.',
        'Layan sketches it on the whiteboard: what happens when many small trim commands add up, and how bad could it be?',
        'Khalid wants a requirement, not a worry: exactly what must the flight-control computer never allow?',
        'The simulator report checks one command at a time. Layan lists the evidence that would show the protection works.',
        'The safety case is due for sign-off. Does its argument even reach repeated trim, or a failed angle-of-attack sensor?'
      ],
      twist: 'Friday 16:00. A simulator trace: in repeated mode, total nose-down trim went past the modelled limit while every individual command stayed within its bound. The sequences came from the AI assistant, which had found that many small commands save fuel.',
      epilogue: 'Monday’s review is waiting. Khalid will sign only a claim with a stated boundary and the evidence behind it. What exactly would your safety claim cover, and what would it not?',
      practice: 'Layan asks an AI chat to play the certification reviewer and attack her argument. It helps her rehearse. The hazard analysis and the safety claim she signs are her own.',
      hook: 'Every command the AI proposed passed its check. Total trim still crossed the line.',
      caseFigure: {src: 'assets/story/ch12-aircraft-trim.svg', alt: 'Airliner with one angle-of-attack sensor and a flight-control computer that limits each trim command; a chart shows every command within its limit while the total trim passes the modelled limit', caption: 'Teaching illustration · select to enlarge'},
      lens: 'A vendor’s AI assistant proposes trim sequences to cut fuel burn. Every command it proposed passed the per-command limiter in the simulator, and test crews now accept them without editing.',
      aiSystem: 'An AI assistant proposes trim sequences. The question for the engineer: does the limit hold whatever the assistant proposes?',
      real: {
        title: 'Boeing 737 MAX · MCAS', when: '2018–2019',
        facts: [
          'MCAS pushed the nose down automatically when it sensed a high angle of attack. It acted on one angle-of-attack sensor at a time.',
          'The safety analysis described at most 0.6° of tail movement per activation. In service it could move 2.5°, and it reset and activated again after each pilot correction.',
          'The design assumed pilots would respond to an unexpected activation within about three seconds.',
          'A faulty sensor led to two crashes: Lion Air 610 (October 2018) and Ethiopian 302 (March 2019). 346 people died, and the fleet was grounded worldwide.'
        ],
        map: [
          ['Reliable but unsafe', 'MCAS did what its specification said, on a wrong sensor value.'],
          ['Single cause in the fault tree', 'One sensor could trigger it: no redundancy on that path.'],
          ['A bound per command is not a bound on the total', 'Each activation was limited; repeated activations drove the nose down.'],
          ['Scope of the safety case', 'The argument covered one 0.6° activation, not repeated 2.5° ones.']
        ],
        lesson: 'The fix compares both sensors, activates once per event and never commands more than pilots can counter. The safety claim now matches what the system can actually do.',
        sources: [['Seattle Times investigation (Gates & Baker, 2019)', 'https://afacwa.org/?p=1143'], ['MCAS overview', 'https://en.wikipedia.org/wiki/Maneuvering_Characteristics_Augmentation_System']]
      }
    },
    13: {
      caseFigure: {src: 'assets/story/ch13-portal-access.svg', alt: 'A portal hides other teams’ links, but a typed document number reaches the server, and no test shows that it refuses; an AI assistant reads every team’s files through one service account', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'The AI assistant reads files through its own service account. The question for the engineer: does the server check access for the person asking, or only for the assistant?',
      real: {
        title: 'First American Financial', when: '2019',
        facts: [
          'A title-insurance website served customer documents at web addresses that ended in a document number.',
          'Changing one digit in the address opened another customer’s documents. No sign-in was needed.',
          'About 885 million documents, dating back to 2003, were exposed: bank statements, Social Security numbers, mortgage and tax records.',
          'KrebsOnSecurity reported it on 24 May 2019, and the company disabled access the same day.'
        ],
        map: [
          ['A hidden link is not access control', 'Nobody saw the links, but the server served any number asked for.'],
          ['Check on the server, on every path', 'The server never asked: may this requester see this document?'],
          ['Test as another user', 'One test as a different customer would have found it in minutes.'],
          ['Over-broad identity', 'Like the assistant’s service account in the story: access was not limited to the asker.']
        ],
        lesson: 'Hiding is not authorising. The server must check every request, on every path, for the person who is asking.',
        sources: [['KrebsOnSecurity, 24 May 2019', 'https://krebsonsecurity.com/2019/05/first-american-financial-corp-leaked-hundreds-of-millions-of-title-insurance-records/']]
      }
    },
    14: {
      caseFigure: {src: 'assets/story/ch14-recovery-identity.svg', alt: 'The backup server runs, but the identity service is down, so staff cannot complete the critical task', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'An AI recovery assistant gives confident instructions it has never rehearsed. The question for the engineer: what evidence shows its steps work in this outage?',
      real: {
        title: 'Maersk · NotPetya', when: '2017',
        facts: [
          'On 27 June 2017, NotPetya malware spread through the network of Maersk, one of the world’s largest shipping companies.',
          'It wiped every domain controller, the identity service that every sign-in depends on, and made about 4,000 servers and 45,000 PCs unusable.',
          'One domain controller in Ghana survived only because a local power cut had taken it offline. Its copy was carried to the recovery team.',
          'Maersk rebuilt in about ten days. The attack cost it an estimated 300 million US dollars.'
        ],
        map: [
          ['A running backup is not a recovered service', 'Servers could be restored, but nothing worked without sign-in.'],
          ['Hidden shared dependency', 'Every system, recovery tools included, depended on the identity service.'],
          ['Recognise, resist, recover, reinstate', 'Recovery hung on one copy that survived by luck.'],
          ['Rehearse the whole service', 'A rehearsal without the identity service would have shown the gap.']
        ],
        lesson: 'Recovery means the essential service works again, not that a server is running. Find what everything depends on before the outage.',
        sources: [['Redmond Magazine: “Domain controller nightmare” (2018)', 'https://redmondmag.com/blogs/scott-bekker/2018/08/domain-controller-nightmare.aspx']]
      }
    },
    15: {
      caseFigure: {src: 'assets/story/ch15-reuse-fit.svg', alt: 'A purchased booking product covers ordinary bookings but not waiting periods or linked follow-ups; an evidence table marks unknown as not met', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'A hosted language model drafts replies, and the tested version will be retired. The question for the engineer: is a model you do not control a component you can rely on?',
      real: {
        title: 'Ariane 5 · Flight 501', when: '1996',
        facts: [
          'Ariane 5 reused the inertial reference software of Ariane 4, which had flown successfully for years.',
          'Ariane 5 flew a faster early trajectory. A horizontal velocity value no longer fitted when converted from a 64-bit floating-point number to a 16-bit integer.',
          'The overflow shut down both inertial reference units, which ran the same reused software.',
          'The rocket veered off course and self-destructed 37 seconds after launch on 4 June 1996. Losses exceeded 370 million US dollars.'
        ],
        map: [
          ['Reuse carries assumptions', 'The code assumed Ariane 4 flight speeds.'],
          ['Proven elsewhere is not fit here', 'Years of success on Ariane 4 said nothing about Ariane 5.'],
          ['Redundancy with a common cause', 'Both units ran the same code and failed together.'],
          ['Evaluate before you commit', 'The new trajectory was never used to test the reused unit.']
        ],
        lesson: 'A reused component brings its old assumptions. Check them against the new system, not against its past success.',
        sources: [['Ariane flight V88', 'https://en.wikipedia.org/wiki/Ariane_flight_V88']]
      }
    },
    16: {
      caseFigure: {src: 'assets/story/ch16-units-contract.svg', alt: 'A sensor sends 95 with no documented unit to an AI forecaster that assumes Celsius', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'An AI forecaster accepts any number without checking its unit. The question for the engineer: what contract must hold at its input?',
      real: {
        title: 'Mars Climate Orbiter', when: '1999',
        facts: [
          'Ground software built by Lockheed Martin reported thruster impulse in pound-force seconds.',
          'NASA’s navigation software expected newton-seconds, so every value was off by a factor of about 4.45.',
          'The interface accepted every number without error. The spacecraft approached Mars at about 57 km instead of the planned 226 km.',
          'It was lost on 23 September 1999. The mission cost 327.6 million US dollars.'
        ],
        map: [
          ['Matching interfaces are not matching meanings', 'Number in, number out; nobody checked the unit.'],
          ['Write the contract', 'The unit was a precondition no one enforced.'],
          ['Test the meaning', 'One test with a known value would have shown the 4.45× gap.'],
          ['Someone owns the seam', 'NASA: the problem was not the error, but the failure to detect it.']
        ],
        lesson: 'A component contract is more than a data type. State units, ranges and meaning, and test across the seam.',
        sources: [['Mars Climate Orbiter', 'https://en.wikipedia.org/wiki/Mars_Climate_Orbiter']]
      }
    },
    17: {
      caseFigure: {src: 'assets/story/ch17-retry-duplicate.svg', alt: 'A booking request times out with its response lost; a retry with a new identifier may book twice', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'A hosted AI service drafts each confirmation, so a retry produces a different message. The question for the engineer: how do you make the side effect safe to repeat?',
      real: {
        title: 'AWS us-east-1 outage', when: '2021',
        facts: [
          'On 7 December 2021, an automated scaling activity in AWS’s main network triggered unexpected behaviour from a large number of clients on its internal network.',
          'A latent issue stopped those clients from backing off. Their retries created a surge of connections that overwhelmed networking devices.',
          'Many services and customer applications in the region were degraded for about seven hours.',
          'AWS disabled the scaling activity and changed the clients’ back-off behaviour.'
        ],
        map: [
          ['Retries are not free', 'Each client retried; together they made the outage worse.'],
          ['Back off and bound retries', 'Clients that cannot back off turn a fault into a flood.'],
          ['A timeout says little', 'A slow reply does not tell you whether the work happened.'],
          ['Make repeats safe', 'A safe retry needs the same request identity, as in the story.']
        ],
        lesson: 'A retry is a new request. Bound it, back off, and make repeated requests safe to run twice.',
        sources: [['AWS post-event summary', 'https://aws.amazon.com/message/12721/']]
      }
    },
    20: {
      caseFigure: {src: 'assets/story/ch20-dashboard-feeds.svg', alt: 'A shared dashboard shows three independently owned feeds, one with its age not shown and one classified by an AI model', caption: 'Teaching illustration · select to enlarge'},
      aiSystem: 'One agency’s feed comes from an AI model nobody outside can inspect. The question for the engineer: what can the dashboard honestly claim about that feed?',
      real: {
        title: 'Northeast blackout', when: '2003',
        facts: [
          'On 14 August 2003, a race condition stalled the alarm system in FirstEnergy’s control room for over an hour.',
          'Operators did not know. Their screens still showed data, but refreshed every 59 seconds instead of every 1–3 seconds.',
          'FirstEnergy did not tell the regional coordinator (MISO) that its view of the grid was degraded.',
          'Failures cascaded across connected systems, and about 55 million people lost power.'
        ],
        map: [
          ['Stale shown as live', 'Screens looked normal while the data behind them aged.'],
          ['No one owns the whole system', 'Neighbouring operators relied on a view they did not control.'],
          ['Agree freshness and failure display', 'Nobody was told the view was degraded.'],
          ['Narrow the claim', 'Knowing which feed is stale lets others act on what is still true.']
        ],
        lesson: 'In a system of systems, show the age of every feed and say when a view is degraded. Silence looks like normal.',
        sources: [['Northeast blackout of 2003', 'https://en.wikipedia.org/wiki/Northeast_blackout_of_2003']]
      }
    }
  };
  for (const k in R) if (S.chapters[k]) Object.assign(S.chapters[k], R[k]);
})(window.ISCARB_STORY);
/* class-builds:begin (generated by tools/apply_class_builds.py) */
(function (S) {
  if (!S) return;
  const B = {
 "12": {
  "question": "The crew sees the nose pushed down. Which single event can cause that on its own, and which of the three tests fail on the current design?",
  "map": [
   [
    10,
    "A fault tree reads logic: OR = any one input is enough; AND = all inputs are needed.",
    "OR(...), AND(...)"
   ],
   [
    17,
    "Check every path to the unsafe exit.",
    "cut_sets(tree) lists every path"
   ],
   [
    11,
    "Make “shall not” checkable.",
    "single_points(tree) == []"
   ]
  ],
  "bridge": "Assignment 3: the same steps for the loading-bay barrier. Build current and revised trees, then test that no single event causes the hazard.",
  "assignment": 3,
  "helpers": "",
  "buggy": "# Hazard: trim pushes the nose down.\n# Current design:\ntree = OR(\n    Event(\"AoA sensor reads wrong\", \"fact\"),\n    AND(Event(\"Trim command repeats\", \"fact\"),\n        Event(\"Crew misses runaway trim\",\n              \"assumption\")),\n)\n",
  "fixed": "# Revised: a second sensor must also miss it.\ntree = OR(\n    AND(Event(\"AoA sensor reads wrong\", \"fact\"),\n        Event(\"Cross-check misses it\",\n              \"proposed\")),\n    AND(Event(\"Trim command repeats\", \"fact\"),\n        Event(\"Crew misses runaway trim\",\n              \"assumption\")),\n)\n",
  "tests": "def test_no_single_event_causes_hazard():\n    assert single_points(tree) == []\n\ndef test_sensor_fault_stays_in_tree():\n    names = [e.name for e in events(tree)]\n    assert \"AoA sensor reads wrong\" in names\n\ndef test_new_control_marked_proposed():\n    tags = [e.source for e in events(tree)]\n    assert \"proposed\" in tags\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_no_single_event_causes_hazard",
      false,
      "assertion failed"
     ],
     [
      "test_sensor_fault_stays_in_tree",
      true,
      ""
     ],
     [
      "test_new_control_marked_proposed",
      false,
      "assertion failed"
     ]
    ],
    "show": "cut_sets(tree)  →  [('AoA sensor reads wrong',), ('Crew misses runaway trim', 'Trim command repeats')]"
   },
   "fixed": {
    "tests": [
     [
      "test_no_single_event_causes_hazard",
      true,
      ""
     ],
     [
      "test_sensor_fault_stays_in_tree",
      true,
      ""
     ],
     [
      "test_new_control_marked_proposed",
      true,
      ""
     ]
    ],
    "show": "cut_sets(tree)  →  [('AoA sensor reads wrong', 'Cross-check misses it'), ('Crew misses runaway trim', 'Trim command repeats')]"
   }
  }
 },
 "13": {
  "question": "The page shows each student only their own link. Which test fails, and why is a hidden link not access control?",
  "map": [
   [
    8,
    "A testable claim names the actor, the action, the object and the evidence.",
    "each test names a user, a grade and the result"
   ],
   [
    13,
    "Test the boundary with a counterexample, not only the normal case.",
    "test_another_student_is_refused"
   ],
   [
    18,
    "An instruction or a hidden link is not an access control.",
    "the server checks role and owner"
   ]
  ],
  "bridge": "Assignment 4: the same steps for the project portal. Write can_read and tests that try to cross the boundary.",
  "assignment": 4,
  "helpers": "",
  "buggy": "def can_view(user, grade):\n    # the page links only your own grade\n    return user.get(\"logged_in\", False)\n",
  "fixed": "def can_view(user, grade):\n    try:\n        role = user[\"role\"]\n        if role == \"student\":\n            return grade[\"student\"] == user[\"id\"]\n        if role == \"instructor\":\n            mine = user[\"courses\"]\n            return grade[\"course\"] in mine\n    except (KeyError, TypeError):\n        pass\n    return False   # fail-safe default\n",
  "tests": "ALI = {\"id\": \"s1\", \"role\": \"student\",\n       \"logged_in\": True}\nSARA = {\"id\": \"s2\", \"role\": \"student\",\n        \"logged_in\": True}\nG = {\"student\": \"s1\", \"course\": \"CPIT-455\"}\n\ndef test_own_grade_is_allowed():\n    assert can_view(ALI, G)\n\ndef test_another_student_is_refused():\n    assert can_view(SARA, G) is False\n\ndef test_broken_request_is_refused():\n    assert can_view({}, G) is False\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_own_grade_is_allowed",
      true,
      ""
     ],
     [
      "test_another_student_is_refused",
      false,
      "assertion failed"
     ],
     [
      "test_broken_request_is_refused",
      true,
      ""
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_own_grade_is_allowed",
      true,
      ""
     ],
     [
      "test_another_student_is_refused",
      true,
      ""
     ],
     [
      "test_broken_request_is_refused",
      true,
      ""
     ]
    ]
   }
  }
 },
 "14": {
  "question": "After the outage, staff merge the paper records back. Which test fails, and what does the student see the next morning?",
  "map": [
   [
    5,
    "Recovery and reinstatement are different jobs.",
    "merge runs at reinstatement"
   ],
   [
    17,
    "A fallback must be reconciled afterwards.",
    "merge(central, offline)"
   ],
   [
    12,
    "An emergency mode must record who acted.",
    "each record keeps its id"
   ]
  ],
  "bridge": "Assignment 5: the same steps for the transport desk. Write reconcile, apply each change once, and report stale changes as conflicts.",
  "assignment": 5,
  "helpers": "",
  "buggy": "def merge(central, offline):\n    # add everything written on paper\n    return central + offline\n",
  "fixed": "def merge(central, offline):\n    seen = {r[\"id\"] for r in central}\n    out = list(central)\n    for r in offline:\n        # identity decides, not content\n        if r[\"id\"] not in seen:\n            seen.add(r[\"id\"])\n            out.append(r)\n    return out\n",
  "tests": "C = [{\"id\": \"r1\", \"who\": \"Huda\"}]\nNEW = {\"id\": \"r2\", \"who\": \"Omar\"}\nSAME = {\"id\": \"r1\", \"who\": \"Huda\"}\n\ndef test_new_offline_record_is_added():\n    assert len(merge(C, [NEW])) == 2\n\ndef test_synced_record_is_not_doubled():\n    assert len(merge(C, [SAME])) == 1\n\ndef test_central_list_is_not_changed():\n    merge(C, [NEW])\n    assert len(C) == 1\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_new_offline_record_is_added",
      true,
      ""
     ],
     [
      "test_synced_record_is_not_doubled",
      false,
      "assertion failed"
     ],
     [
      "test_central_list_is_not_changed",
      true,
      ""
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_new_offline_record_is_added",
      true,
      ""
     ],
     [
      "test_synced_record_is_not_doubled",
      true,
      ""
     ],
     [
      "test_central_list_is_not_changed",
      true,
      ""
     ]
    ]
   }
  }
 },
 "15": {
  "question": "The vendor’s brochure mentions single sign-on. Which test fails, and what is the difference between a claim and evidence?",
  "map": [
   [
    8,
    "“Configurable” is a capability claim; only a demonstrated instance shows fit.",
    "brochure ≠ demonstrated"
   ],
   [
    15,
    "Compare reuse routes by the test that would prove them.",
    "status returns unknown"
   ],
   [
    17,
    "A wrapper hides the interface, not the assumptions.",
    "the unchecked feature stays unknown"
   ]
  ],
  "bridge": "Assignment 6: the same steps for the booking system. Write fit, shortlist and evidence_needed from the supplied facts only.",
  "assignment": 6,
  "helpers": "SOURCES = {\"arabic-ui\": \"demonstrated\",\n           \"single-sign-on\": \"brochure\"}\n",
  "buggy": "def status(feature):\n    # anything the vendor mentions counts\n    if feature in SOURCES:\n        return \"met\"\n    return \"unknown\"\n",
  "fixed": "def status(feature):\n    # only a demonstrated instance counts\n    if SOURCES.get(feature) == \"demonstrated\":\n        return \"met\"\n    return \"unknown\"\n",
  "tests": "def test_demonstrated_feature_is_met():\n    assert status(\"arabic-ui\") == \"met\"\n\ndef test_brochure_claim_is_not_evidence():\n    assert status(\"single-sign-on\") == \"unknown\"\n\ndef test_unchecked_feature_is_unknown():\n    assert status(\"export\") == \"unknown\"\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_demonstrated_feature_is_met",
      true,
      ""
     ],
     [
      "test_brochure_claim_is_not_evidence",
      false,
      "assertion failed"
     ],
     [
      "test_unchecked_feature_is_unknown",
      true,
      ""
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_demonstrated_feature_is_met",
      true,
      ""
     ],
     [
      "test_brochure_claim_is_not_evidence",
      true,
      ""
     ],
     [
      "test_unchecked_feature_is_unknown",
      true,
      ""
     ]
    ]
   }
  }
 },
 "16": {
  "question": "The app sends litres; the pump expects millilitres. The types match. Which tests fail?",
  "map": [
   [
    9,
    "A number type is only syntax: state the unit, range and meaning.",
    "litres × 1000 = ml"
   ],
   [
    16,
    "Preconditions before the call, postconditions after it.",
    "ValueError before, RuntimeError after"
   ],
   [
    12,
    "Ariane: earlier success does not carry over to a new context.",
    "test the new range"
   ]
  ],
  "bridge": "Assignment 7: the same steps for the room-booking component. Write reserve_minutes: precondition, conversion, postcondition.",
  "assignment": 7,
  "helpers": "class Pump:\n    \"\"\"Contract: infuse(ml), 1 to 5000 ml.\"\"\"\n    def __init__(self):\n        self.calls = []\n    def infuse(self, ml):\n        self.calls.append(ml)\n        return ml\n",
  "buggy": "def give(pump, litres):\n    # the types match: a number is a number\n    return pump.infuse(litres)\n",
  "fixed": "def give(pump, litres):\n    # precondition: before the call\n    ok = type(litres) in (int, float)\n    if not (ok and 0.001 <= litres <= 5):\n        raise ValueError(\"0.001 to 5 litres\")\n    ml = round(litres * 1000)\n    # postcondition: on the result\n    if pump.infuse(ml) != ml:\n        raise RuntimeError(\"pump broke contract\")\n    return ml\n",
  "tests": "def test_half_litre_is_500_ml():\n    p = Pump()\n    give(p, 0.5)\n    assert p.calls == [500]\n\ndef test_too_much_refused_before_call():\n    p = Pump()\n    try:\n        give(p, 9)\n        assert False, \"accepted\"\n    except ValueError:\n        assert p.calls == []\n\ndef test_zero_is_refused():\n    p = Pump()\n    try:\n        give(p, 0)\n        assert False, \"accepted\"\n    except ValueError:\n        assert p.calls == []\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_half_litre_is_500_ml",
      false,
      "assertion failed"
     ],
     [
      "test_too_much_refused_before_call",
      false,
      "assertion failed: accepted"
     ],
     [
      "test_zero_is_refused",
      false,
      "assertion failed: accepted"
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_half_litre_is_500_ml",
      true,
      ""
     ],
     [
      "test_too_much_refused_before_call",
      true,
      ""
     ],
     [
      "test_zero_is_refused",
      true,
      ""
     ]
    ]
   }
  }
 },
 "17": {
  "question": "The reply to a payment is lost and the app retries. Which tests fail, and how much is the customer charged?",
  "map": [
   [
    7,
    "A timeout does not tell you whether the work happened.",
    "test_retry_after_lost_reply"
   ],
   [
    9,
    "Keep the uncertainty visible; record the outcome before replying.",
    "done[request_id]"
   ],
   [
    19,
    "A retry is a new request unless it carries the same identity.",
    "the same request_id"
   ]
  ],
  "bridge": "Assignment 8: the same steps for event registration. Make reserve idempotent, including after a restart.",
  "assignment": 8,
  "helpers": "",
  "buggy": "class Payments:\n    def __init__(self, store):\n        self.store = store\n        store.setdefault(\"charges\", [])\n    def pay(self, request_id, amount):\n        # every call charges\n        self.store[\"charges\"].append(amount)\n        return len(self.store[\"charges\"])\n",
  "fixed": "class Payments:\n    def __init__(self, store):\n        self.store = store\n        store.setdefault(\"charges\", [])\n        store.setdefault(\"done\", {})\n    def pay(self, request_id, amount):\n        done = self.store[\"done\"]\n        if request_id in done:   # a retry\n            return done[request_id]\n        self.store[\"charges\"].append(amount)\n        done[request_id] = len(done) + 1\n        return done[request_id]\n",
  "tests": "def test_two_payments_two_charges():\n    st = {}\n    p = Payments(st)\n    p.pay(\"a\", 50)\n    p.pay(\"b\", 50)\n    assert len(st[\"charges\"]) == 2\n\ndef test_retry_after_lost_reply():\n    st = {}\n    p = Payments(st)\n    p.pay(\"a\", 50)\n    p.pay(\"a\", 50)   # same request id\n    assert len(st[\"charges\"]) == 1\n\ndef test_retry_after_restart():\n    st = {}\n    Payments(st).pay(\"a\", 50)\n    Payments(st).pay(\"a\", 50)   # new process\n    assert len(st[\"charges\"]) == 1\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_two_payments_two_charges",
      true,
      ""
     ],
     [
      "test_retry_after_lost_reply",
      false,
      "assertion failed"
     ],
     [
      "test_retry_after_restart",
      false,
      "assertion failed"
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_two_payments_two_charges",
      true,
      ""
     ],
     [
      "test_retry_after_lost_reply",
      true,
      ""
     ],
     [
      "test_retry_after_restart",
      true,
      ""
     ]
    ]
   }
  }
 },
 "20": {
  "question": "The lift feed lost its connection ten minutes ago. Which tests fail, and what does the dashboard tell the duty officer?",
  "map": [
   [
    13,
    "When a feed fails, show what is missing or stale; do not hide it.",
    "unavailable / stale, 9 min old"
   ],
   [
    8,
    "Promise what the dashboard controls; label what it only receives.",
    "the label shows the age"
   ],
   [
    15,
    "Data feeds need bounded waits and agreed formats.",
    "limit=5"
   ]
  ],
  "bridge": "Assignment 9: the same steps for the incident dashboard. Write display_state and headline, and never call a degraded view live.",
  "assignment": 9,
  "helpers": "",
  "buggy": "def label(feed, now, limit=5):\n    # the last value always looks live\n    return f\"{feed['name']}: live\"\n",
  "fixed": "def label(feed, now, limit=5):\n    name, at = feed[\"name\"], feed.get(\"at\")\n    if not feed.get(\"connected\") or at is None:\n        return f\"{name}: unavailable\"\n    age = now - at\n    if age <= limit:\n        return f\"{name}: live\"\n    return f\"{name}: stale, {age} min old\"\n",
  "tests": "F = {\"name\": \"Lifts\", \"connected\": True,\n     \"at\": 100}\nLOST = dict(F, connected=False)\n\ndef test_fresh_feed_is_live():\n    assert label(F, 103) == \"Lifts: live\"\n\ndef test_old_feed_shows_its_age():\n    assert \"9 min old\" in label(F, 109)\n\ndef test_lost_feed_is_not_live():\n    assert label(LOST, 101) == \"Lifts: unavailable\"\n",
  "result": {
   "buggy": {
    "tests": [
     [
      "test_fresh_feed_is_live",
      true,
      ""
     ],
     [
      "test_old_feed_shows_its_age",
      false,
      "assertion failed"
     ],
     [
      "test_lost_feed_is_not_live",
      false,
      "assertion failed"
     ]
    ]
   },
   "fixed": {
    "tests": [
     [
      "test_fresh_feed_is_live",
      true,
      ""
     ],
     [
      "test_old_feed_shows_its_age",
      true,
      ""
     ],
     [
      "test_lost_feed_is_not_live",
      true,
      ""
     ]
    ]
   }
  }
 }
};
  for (const k in B) if (S.chapters[k]) S.chapters[k].build = B[k];
})(window.ISCARB_STORY);
/* class-builds:end */
