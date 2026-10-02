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
 lead: {name: 'Layan', role: 'Junior software engineer at a Jeddah engineering consultancy · your seat in the story'},
 mentor: {name: 'Khalid', role: 'Senior engineer · her mentor · always asks “what is your evidence?”'},
 chapters: {
  10: {
   episode: 'Episode 1 · The alarm at 02:10',
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
   episode: 'Episode 2 · Release on Thursday',
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
   episode: 'Episode 3 · Every command within limits',
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
   episode: 'Episode 4 · The record that crossed the line',
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
   episode: 'Episode 5 · 02:00, and nobody can sign in',
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
   episode: 'Episode 6 · Buy, bend or build',
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
   episode: 'Episode 7 · Ninety-five degrees',
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
   episode: 'Episode 8 · Did it go through?',
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
   episode: 'Episode 9 · Whose dashboard is it?',
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
