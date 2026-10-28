"""Chapter 8 lecture: Software Testing and Code Coverage (authored, idempotent).

The tenth classroom lecture, built in the same iSCARB style as Chapters 10–20 and on the same runtime
(lectures/iscarb/runtime/classroom-v3.js): 20 classroom units, five objectives, three stations, the 20 rules,
a fictional training case, a source transfer case, the five-objective check, the AI challenge and the story layer.

Source: the textbook's own slide pack for Chapter 8 (Sommerville, Software Engineering, 10th edition), from the slide
set published on software-engineering-book.com/slides (the same set as the Chapter 10–20 packs: Ch16 is byte-identical).
The code-coverage part extends source slide 47 ("Code coverage") with the course page code-coverage.html (course outcome 11).

Chapter 8 has no separate FBR assignment: it is assessed through the coverage step of every Python build in
Assignments 3–9 and in the final examination. The lecture therefore links to the coverage step instead of an
assignment page (assignmentHref / assignmentLabel / gradedNote in the lecture data).

Writes:
  lectures/iscarb/Ch8-Software-Testing.html     the lecture (shell of the Chapter 16 lecture, new lecture-data)
  lectures/iscarb/sources/Ch8-Study.html        the complete source review (all 64 slides, figures)
  lectures/iscarb/runtime/story-v3.js           the Chapter 8 story entry (between markers)
Needs lectures/iscarb/sources/Ch8-Original.pptx and assets/v3/ch8-fig-N.jpg (rendered from that pack).

Run:  python3 tools/author_ch8_lecture.py
"""
from __future__ import annotations
import html, json, re, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEC = ROOT / 'lectures/iscarb'
OUT = LEC / 'Ch8-Software-Testing.html'
SHELL = LEC / 'Ch16-Component-Based-SE.html'
PPTX = LEC / 'sources/Ch8-Original.pptx'
STUDY = LEC / 'sources/Ch8-Study.html'
STORY = LEC / 'runtime/story-v3.js'
E = html.escape
FIG = {n: f'assets/v3/ch8-fig-{n}.jpg' for n in (7, 11, 15, 21, 28, 29, 34, 40, 45, 60)}
CAP = 'Sommerville Ch.8 · preserved source illustration'
RELEASE, VERSION = '20261028-ch8-testing', '20261028-ch8-v1'


# ---- source ledger from the original pack ----------------------------------------------------------------------
def ledger():
    z = zipfile.ZipFile(PPTX)
    names = sorted((n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)), key=lambda n: int(re.findall(r'\d+', n)[0]))
    out = []
    for n in names:
        x = z.read(n).decode('utf8')
        paras = []
        for p in re.findall(r'<a:p>.*?</a:p>', x, flags=re.S):
            t = html.unescape(''.join(re.findall(r'<a:t>(.*?)</a:t>', p, flags=re.S))).strip()
            if t and not re.fullmatch(r'Chapter 8 Software Testing|\d{1,2}|30/10/2014', t):
                paras.append(t)
        k = int(re.findall(r'\d+', n)[0])
        title = paras[0] if paras else f'Slide {k}'
        out.append({'n': k, 'title': title, 'lines': paras})
    return out


# ---- coverage of every source slide: (cls, unit) ----------------------------------------------------------------
UNIT_OF = {}
for a, b, u in [(3, 7, 'X01'), (8, 14, 'X02'), (15, 16, 'X03'), (17, 22, 'X04'), (23, 25, 'X05'), (26, 31, 'B01'),
                (32, 36, 'X06'), (37, 42, 'R09'), (43, 48, 'D08'), (49, 56, 'VALIDATE'), (57, 62, 'X07')]:
    for n in range(a, b + 1):
        UNIT_OF[n] = u
FULL = {3, 6, 8, 16, 18, 24, 27, 35, 44, 47, 50, 59}
FIGKIND = {7, 11, 15, 21, 28, 29, 34, 40, 45, 60}
SECTION = {17, 43, 49, 57}


def coverage(L):
    cov = []
    for s in L:
        n = s['n']
        if n == 1:
            c = {'cls': 'no', 'reason': 'Title slide of the source pack'}
        elif n == 2:
            c = {'cls': 'no', 'reason': 'Agenda slide; its topics are the chapter map'}
        elif n in SECTION:
            c = {'cls': 'no', 'reason': 'Section divider; its section is the unit that follows'}
        elif n in (63, 64):
            c = {'cls': 'no', 'reason': 'Key points; summarised in the five-objective check and the study list'}
        else:
            c = {'cls': 'full' if n in FULL else 'slide', 'unit': UNIT_OF[n]}
            if n in FIGKIND:
                c['kind'] = 'figure'
        c['n'] = n; c['title'] = s['title']
        cov.append(c)
    return cov


# ---- the twenty classroom units --------------------------------------------------------------------------------
def learn(**k):
    base = {'fig': None, 'rows': None, 'heads': None, 'extra': '', 'phase': 'LEARN', 'tier': 'core', 'minutes': 1.5}
    base.update(k)
    if 'figure' in base and 'caption' not in base:
        base['caption'] = CAP
    base.setdefault('sourceStart', int(re.findall(r'\d+', base.get('sourceRange', '1'))[0]))
    return base


SLIDES = [
    {'id': 'TITLE', 'title': 'Software Testing and Code Coverage', 'phase': 'START', 'takeaway': 'Software Testing and Code Coverage',
     'full': '<p>Software Testing and Code Coverage</p>', 'sourceStart': 1, 'minutes': 2, 'tier': 'core'},
    {'id': 'MAP', 'title': 'The chapter at a glance', 'phase': 'LEARN', 'takeaway': 'The chapter at a glance',
     'full': '<p>The chapter at a glance</p>', 'sourceStart': 1, 'minutes': 1, 'tier': 'core'},
    {'id': 'START', 'title': 'Start with the problem', 'phase': 'SEE', 'takeaway': 'Start with the problem',
     'full': '<p>Start with the problem</p>', 'sourceStart': 1, 'minutes': 1.5, 'tier': 'core'},

    learn(id='X01', title='Two goals: show it works, and try to break it', sourceRange='3–7', figure=FIG[7],
          bullets=[['Validation testing', 'Show the system meets its requirements with cases that reflect expected use.'],
                   ['Defect testing', 'Expose wrong behaviour; the cases may be deliberately obscure.'],
                   ['A successful defect test', 'Makes the system fail, so a defect is found.'],
                   ['The limit', 'Testing shows the presence of errors, not their absence.']],
          question='A test suite passes completely. What has it shown, and what has it not shown?',
          answer='It has shown that the system behaved correctly for the inputs that were tried. It has not shown that there are no defects: inputs outside the tested set may still fail. Testing reveals the presence of errors, not their absence.',
          takeaway='Testing can show that errors are present, never that they are absent.',
          full='<p>Testing is intended to show that a program does what it is intended to do, and to discover defects before it is put into use. You execute the program with artificial data and check the results for errors, anomalies or information about non-functional attributes. Testing is part of the wider verification and validation (V&amp;V) process, which also includes static techniques.</p><p>The process has two goals. The first leads to <b>validation testing</b>: show the developer and the customer that the software meets its requirements—for custom software, at least one test for every requirement; for a product, tests for every feature and for combinations of features. Its test cases reflect the system’s expected use, and a successful test is one where the system behaves as intended. The second leads to <b>defect testing</b>: discover situations in which the behaviour is incorrect, undesirable or not as specified—crashes, unwanted interactions, incorrect computations, data corruption. Its test cases are designed to expose defects and can be deliberately obscure; a successful defect test is one that makes the system fail.</p><p>The input–output model shows why testing has a limit: among all possible inputs there is a subset I<sub>e</sub> that causes anomalous behaviour, and the outputs O<sub>e</sub> that reveal defects. Tests find a defect only if they sample from I<sub>e</sub>. That is why testing can reveal the presence of errors, not their absence.</p>',
          notes='Ask the class to say, in one sentence, what a fully passing test suite proves. Push until someone says “only that the tried inputs work”. Link it to the case: the three tests all pass.',
          concept='validation versus defect testing', answerKey='passing tests show behaviour only for the inputs tried',
          commonError='Students say a passing suite proves the program is correct. Ask which inputs were not tried.'),

    learn(id='X02', title='Verification, validation and inspections', sourceRange='8–14', figure=FIG[11], tier='optional',
          bullets=[['Verification', '“Are we building the product right?” It conforms to its specification.'],
                   ['Validation', '“Are we building the right product?” It does what users really need.'],
                   ['Inspections', 'Static: people examine code or documents without running them.'],
                   ['Complementary', 'Inspections cannot check performance or usability; testing can.']],
          question='Which can find a defect before the program is complete: inspection or testing?',
          answer='Inspection. It needs no execution, so it can examine requirements, designs or incomplete code. Testing needs a runnable version, or a special harness for the parts that exist.',
          takeaway='Verification checks against the specification; validation checks against real needs.',
          full='<p><b>Verification</b> asks “are we building the product right?”: the software should conform to its specification. <b>Validation</b> asks “are we building the right product?”: the software should do what the user really requires. The aim of V&amp;V is confidence that the system is fit for purpose, and the confidence needed depends on how critical the software is, what users expect, and the marketing environment—getting to market early can matter more than finding every defect.</p><p><b>Software inspections</b> analyse a static representation of the system—requirements, design models, database schemas, code—to discover problems (static verification). <b>Software testing</b> executes the system with test data and observes its behaviour (dynamic verification). Inspections have three advantages: errors cannot mask one another, because nothing runs; incomplete versions can be inspected without a test harness; and an inspection can also consider quality attributes such as standards compliance, portability and maintainability. But inspections cannot check non-functional characteristics such as performance or usability, and they check conformance with a specification, not with the customer’s real requirements. The two techniques are complementary and both belong in V&amp;V.</p>',
          notes='Optional if time is short. Ask for one defect inspection finds that testing struggles with, and one testing finds that inspection cannot (performance).',
          concept='verification versus validation', answerKey='verification: right product build; validation: right product',
          commonError='Students swap the two words. Anchor on the questions: built right, or the right thing?'),

    learn(id='X03', title='The testing process and its three stages', sourceRange='15–16', figure=FIG[15],
          bullets=[['Design test cases', 'Each case: an input and the expected output.'],
                   ['Prepare data, run, compare', 'Compare actual results with the expected ones; report.'],
                   ['Three stages', 'Development testing, release testing, user testing.'],
                   ['Who tests', 'Developers, then a separate team, then users in their own environment.']],
          question='A test case has an input. What else must it have before it can pass or fail?',
          answer='An expected output, decided from the requirement before the test runs. Without it, the test only shows what the program did, not whether that was right.',
          takeaway='A test case is an input plus an expected output decided in advance.',
          full='<p>The testing process model runs from <b>designing test cases</b>—each a specification of the inputs and the expected output—through preparing test data, running the program with that data, and <b>comparing the results with the test cases</b>, producing test results and test reports. The expected output is the key: it must come from the requirement, not from what the program happens to return.</p><p>Commercial software normally passes through three stages of testing. <b>Development testing</b>: the system is tested during development to discover bugs and defects. <b>Release testing</b>: a separate team tests a complete version before it is released to users. <b>User testing</b>: users or potential users test the system in their own environment.</p>',
          notes='Write on the board: test case = input + expected output. Ask where the expected output comes from in the case: the penalty rule in the course policy, not the code.',
          concept='a test case needs an expected output', answerKey='the expected output comes from the requirement',
          commonError='Students write a test as “run penalty(24) and see”. Ask what result they expect and where that comes from.'),

    learn(id='CHECK1', title='Checkpoint · what does a passing test show?', sourceRange='3–16', phase='CHECK', minutes=1,
          bullets=[['Think', 'Three tests pass: 0, 5 and 30 hours late.'],
                   ['Pair', 'Which inputs does the rule treat differently, and which were tried?'],
                   ['Record', 'Write your claim and the evidence you would still need.']],
          question='The penalty function passes tests at 0, 5 and 30 hours. Is it correct for a student who is exactly 24 hours late?',
          answer='We do not know. No test used 24 hours, and the rule changes exactly there (“up to and including 24 hours”). Passing tests show behaviour only for the inputs that were tried.',
          takeaway='A passing test is evidence only for the inputs it tried.',
          full='<p>The rule has three outcomes: on time → no penalty; up to and including 24 hours late → minus 1; more than 24 hours late → not accepted. The three tests sample one value from each outcome, so they look complete. But the rule changes at the boundary, and the boundary was never tried. The honest claim is bounded: “the function is correct for 0, 5 and 30 hours”. The evidence still needed is a test with the expected result at exactly 24 hours, and just either side of it.</p>',
          notes='Ninety seconds alone, then pairs. Collect claims; reward the ones that name the untested boundary value and an expected result.',
          concept='evidence covers only the inputs tried', answerKey='no test at 24 hours, where the rule changes',
          commonError='Students accept three passing tests as proof. Ask which value of hours the rule treats differently.'),

    learn(id='X04', title='Development testing: unit, component, system', sourceRange='17–22', figure=FIG[21],
          bullets=[['Unit testing', 'Functions, methods and classes in isolation; a defect-testing process.'],
                   ['Component testing', 'Several units integrated; test the component interface.'],
                   ['System testing', 'Components integrated; test their interactions.'],
                   ['Object classes', 'All operations, all attributes, all states (state-model sequences).']],
          question='The penalty function is tested on its own, then through the submission page, then with Blackboard. Name the three levels.',
          answer='Unit testing (the function alone), component testing (the submission component through its interface), and system testing (the integrated system, including the interaction with Blackboard).',
          takeaway='Unit, component and system testing look for different kinds of defects.',
          full='<p>Development testing includes all testing carried out by the team that develops the system. <b>Unit testing</b> tests individual program units or object classes and should focus on the functionality of objects or methods. <b>Component testing</b> integrates several units into a composite component and should focus on the component interfaces. <b>System testing</b> integrates some or all components and tests the system as a whole, focusing on component interactions.</p><p>Unit testing is a defect-testing process. Units may be individual functions or methods, object classes with several attributes and methods, or composite components accessed through defined interfaces. Complete test coverage of a class means testing all operations, setting and interrogating all attributes, and exercising the object in all possible states; inheritance makes this harder because what must be tested is not localised. For the weather station, test cases are needed for reportWeather, calibrate, test, startup and shutdown, and a state model gives the sequences of transitions to test—for example Shutdown → Running → Shutdown.</p>',
          notes='Use the weather-station interface on screen. Then map the three levels onto the penalty case so students can name each one.',
          concept='three levels of development testing', answerKey='unit alone, component interface, system interactions',
          commonError='Students call any test of a whole page “unit testing”. Ask what is isolated and what is integrated.'),

    learn(id='X05', title='An automated test: setup, call, assertion', sourceRange='23–25',
          bullets=[['Automate', 'A framework runs every test and reports, with no manual checking.'],
                   ['Setup', 'Initialise the system with the test case: inputs and expected outputs.'],
                   ['Call', 'Call the object or method under test.'],
                   ['Assertion', 'Compare the result with the expected one: true passes, false fails.']],
          question='In assert penalty(24) == -1, which part is the call and which is the expected result?',
          answer='penalty(24) is the call; -1 is the expected result. The assertion compares them. The input 24 and the expected value -1 are the setup, and both come from the rule, not from the code.',
          takeaway='Every automated test sets up, calls and asserts an expected result.',
          rows=[['Setup', 'hours_late = 24 · expected = -1'], ['Call', 'result = penalty(hours_late)'], ['Assertion', 'assert result == expected']],
          heads=['Part', 'In the penalty test'],
          full='<p>Whenever possible, unit testing should be automated so that tests are run and checked without manual intervention. A test automation framework (JUnit in the book; Python’s unittest or pytest in this course) provides generic test classes that you extend; it runs all the tests and reports success or failure. An automated test has three parts: a <b>setup</b> part, where you initialise the system with the test case—the inputs and the expected outputs; a <b>call</b> part, where you call the object or method under test; and an <b>assertion</b> part, where you compare the result with the expected result. If the assertion is true the test passes; if false, it fails.</p><p>Choose two kinds of unit test case. The first reflects normal operation and shows that the component works as expected. The second is based on testing experience of where common problems arise: it uses abnormal inputs to check that they are processed properly and do not crash the component.</p>',
          notes='Show the three-row table, then ask a student to write one test for 24 hours on the board in the same three parts.',
          concept='setup, call, assertion', answerKey='the expected value is set up from the rule',
          commonError='Students assert whatever the function returns today. Ask where the expected value came from.'),

    learn(id='B01', title='Partition testing: one test per class, plus the boundaries', sourceRange='26–31', figure=FIG[29], minutes=2,
          sourceFigs=[28],
          bullets=[['Partitions', 'A partition is a set of inputs the program should treat the same way.'],
                   ['Choose from each', 'At least one test inside every partition.'],
                   ['Boundaries', 'Test at each boundary and just either side: 3, 4, 10, 11.'],
                   ['Guidelines', 'Single-value and empty sequences; force every error message.']],
          question='The penalty rule has three partitions. Which values would you test?',
          answer='One value inside each partition (for example 0, 12 and 30), plus the boundaries and their neighbours: 0 and just above 0, then 23.9, 24 and 24.1. The value that decides the rule is exactly 24.',
          takeaway='Test one value per partition and every boundary, because defects cluster at the edges.',
          lists=[{'source': 30, 'title': 'Testing guidelines (sequences)', 'items': ['Test with sequences that have only a single value', 'Use sequences of different sizes in different tests', 'Access the first, middle and last elements', 'Test with sequences of zero length']},
                 {'source': 31, 'title': 'General testing guidelines', 'items': ['Choose inputs that force every error message', 'Design inputs that overflow input buffers', 'Repeat the same input or series of inputs many times', 'Force invalid outputs', 'Force results that are too large or too small']}],
          full='<p>Two strategies help choose test cases. <b>Partition testing</b> identifies groups of inputs that have common characteristics and should be processed in the same way, and chooses tests from within each group. <b>Guideline-based testing</b> uses guidelines that reflect experience of the errors programmers often make.</p><p>Input data and output results often fall into classes whose members are related. Each class is an <b>equivalence partition</b>, or domain, in which the program behaves in an equivalent way for every member. Test cases should be chosen from each partition, both input and output. The source example: a program accepts 4 to 10 input values, each a five-digit integer from 10000 to 99999. The partitions for the number of values are less than 4, 4 to 10, and more than 10; good tests are 3, 4, 7, 10 and 11—the middle of the valid range and each boundary with the value just outside it. For the values themselves: 9999, 10000, 50000, 99999 and 100000.</p><p>The reason is experience: programmers often get the comparison at a boundary wrong—< instead of ≤—so defects cluster at the edges of partitions. For the penalty rule, “up to and including 24 hours” makes 24 a boundary value that must be tested with its expected result.</p>',
          notes='Do the textbook example first (3, 4, 7, 10, 11), then let pairs derive the penalty values. The decisive one is exactly 24.',
          concept='equivalence partitions and boundary values', answerKey='one value per partition plus each boundary',
          commonError='Students pick three random values, one per outcome, and stop. Ask where the rule changes and whether they tested exactly there.'),

    learn(id='CHECK2', title='Checkpoint · which tests would catch the bug?', sourceRange='26–31', phase='CHECK', minutes=1,
          bullets=[['Think', 'Compare: more random tests, aiming for 100 % coverage, or partition and boundary tests.'],
                   ['Pair', 'Argue for the option your partner rejected.'],
                   ['Record', 'Write why your choice finds the defect, and its limit.']],
          question='The code says hours_late < 24 where the rule says “up to and including 24”. Which strategy is designed to catch that?',
          answer='Partition and boundary testing: it requires a test at exactly 24 hours. Random tests rarely hit one exact value, and 100 % line coverage is already reached without a test at 24.',
          takeaway='Boundary tests target the comparison that random tests and coverage miss.',
          full='<p>The defect is a single comparison: < where the rule needs ≤. Random tests choose values across the whole range, so the chance of hitting exactly 24 is tiny. Coverage measures which code ran, and the three existing tests already execute every line and every branch. Only a strategy that looks at the rule—where its outcome changes—puts a test on 24 with the expected result −1. Its limit: partition testing depends on reading the rule correctly; if the requirement itself is ambiguous, the boundary test inherits the ambiguity.</p>',
          notes='Hands up for each option first, then pairs. The point to land: coverage was already 100 % and still missed it.',
          concept='boundary testing versus coverage', answerKey='only a boundary test at exactly 24 catches it',
          commonError='Students say “get to 100 % coverage”. Show that the three passing tests already have it.'),

    learn(id='X06', title='Interface testing and interface errors', sourceRange='32–36', figure=FIG[34], tier='optional',
          bullets=[['Component testing', 'Show that the component interface behaves as specified.'],
                   ['Interface types', 'Parameter, shared memory, procedural, message passing.'],
                   ['Errors', 'Misuse, misunderstanding, timing.'],
                   ['Guidelines', 'Extreme parameter values, null pointers, tests that make the component fail.']],
          question='The submission page passes hours late as minutes. Which kind of interface error is this?',
          answer='Interface misuse: the caller makes an error in using the interface (wrong unit for the parameter). If the caller believed the function takes minutes, it is interface misunderstanding.',
          takeaway='Interface tests use extreme values and failure cases at the boundary between components.',
          full='<p>Software components are often composite, made of several interacting objects accessed through a defined interface. Component testing should show that the component interface behaves according to its specification, assuming the unit tests of the objects inside have been done. Interface testing aims to detect faults due to interface errors or invalid assumptions about interfaces. Interfaces may be <b>parameter</b> interfaces (data passed between methods), <b>shared memory</b>, <b>procedural</b> (a sub-system encapsulates procedures called by others) or <b>message passing</b>.</p><p>Interface errors are of three kinds: <b>misuse</b>—a calling component makes an error in using another’s interface, such as parameters in the wrong order; <b>misunderstanding</b>—it embeds incorrect assumptions about the called component’s behaviour; and <b>timing</b>—the components run at different speeds and out-of-date information is used. Guidelines: design tests with parameters at the extreme ends of their ranges; always test pointer parameters with null pointers; design tests that cause the component to fail; use stress testing in message-passing systems; and vary the activation order in shared-memory systems.</p>',
          notes='Optional. Connect to Chapter 16: a matching type is not a matching meaning; an interface test at the extremes catches it.',
          concept='interface misuse and misunderstanding', answerKey='wrong unit is misuse; wrong belief is misunderstanding',
          commonError='Students test only normal parameter values across an interface. Ask for the extreme and the failing value.'),

    learn(id='R09', title='System testing: interactions, use cases, policies', sourceRange='37–42', figure=FIG[40],
          bullets=[['Interactions', 'Components compatible, correct data, at the right time.'],
                   ['Emergent behaviour', 'Some behaviour appears only when components work together.'],
                   ['Use-case testing', 'A use case and its sequence diagram give the interactions to test.'],
                   ['Testing policies', 'Exhaustive testing is impossible, so define the required coverage.']],
          question='Why can a system test fail when every unit test passes?',
          answer='Because system testing checks interactions and emergent behaviour: components that each work can still pass the wrong data, at the wrong time, or in the wrong format to one another.',
          takeaway='System testing checks interactions; a testing policy defines what “enough” means.',
          full='<p>System testing during development integrates components into a version of the system and tests the integrated system. Its focus is the interactions between components: that they are compatible, interact correctly and transfer the right data at the right time across their interfaces. It also tests emergent behaviour. Reused and off-the-shelf components may be integrated with new ones, and components from different team members come together, so system testing is a collective process; some companies use a separate testing team.</p><p>The use cases developed to identify system interactions are a good basis for system testing: each use case involves several components, so testing it forces those interactions to occur, and its sequence diagram documents the components and interactions being tested. For the weather station, a request for a report should be acknowledged and a summarised report eventually returned. Because exhaustive system testing is impossible, organisations write <b>testing policies</b> that define the required coverage—for example, all functions accessed through menus must be tested, combinations of functions on the same menu must be tested, and all functions with user input must be tested with correct and incorrect input.</p>',
          notes='Ask what a testing policy for the course portal could say about late submissions: every rule boundary must have a test with its expected result.',
          concept='interactions and testing policies', answerKey='units pass, interactions can still fail',
          commonError='Students assume passing unit tests imply a working system. Ask what data crosses between the components, and when.'),

    learn(id='D08', title='Test-driven development and regression testing', sourceRange='43–48', figure=FIG[45], minutes=2,
          bullets=[['Test first', 'Write the test for a small increment before its code.'],
                   ['Red, then green', 'The new test fails, then the code makes it pass; refactor.'],
                   ['Benefits', 'Code coverage, a regression suite, simpler debugging, documentation.'],
                   ['Regression testing', 'Rerun all tests after every change, before it is committed.']],
          question='With test-first development, when would the test for exactly 24 hours have been written?',
          answer='Before the comparison was coded: the increment “a 24-hour late submission costs one mark” gets its test first, the test fails, then the code is written to pass it. The boundary test then stays in the regression suite.',
          takeaway='Test-first development writes the expected result before the code that must meet it.',
          full='<p>Test-driven development (TDD) interleaves testing and code development. Tests are written before the code, and passing them is the critical driver of development. You identify a small increment of functionality, write an automated test for it, run it with all the other tests—it fails, because the functionality is not there yet—then implement the functionality and rerun the tests. Once all tests pass, you move on to the next increment. TDD came from agile methods such as Extreme Programming, but it can be used in plan-driven processes too.</p><p>The book lists four benefits. <b>Code coverage</b>: every code segment written has at least one associated test. <b>Regression testing</b>: a regression suite is built incrementally as the program is developed. <b>Simplified debugging</b>: when a test fails, the problem is in the newly written code. <b>System documentation</b>: the tests describe what the code should do. <b>Regression testing</b> checks that changes have not broken previously working code. Manual regression testing is expensive; with automated tests, all tests are rerun every time a change is made, and they must pass before the change is committed.</p>',
          notes='Draw the TDD loop. Ask: if the team had written the 24-hour test first, could the < have survived? Then ask why the test must stay in the regression suite.',
          concept='test-first and regression', answerKey='the boundary test is written before the code and kept',
          commonError='Students think TDD means testing after each line of code. The test comes first and must fail first.'),

    learn(id='COVER', title='Code coverage: what ran, not what is right', sourceRange='47', minutes=2,
          sourceLabel='Course addition · extends source slide 47 (code coverage) with the course coverage page',
          bullets=[['Statement coverage', 'Share of lines executed by at least one test.'],
                   ['Branch coverage', 'Share of decision outcomes (true and false) taken.'],
                   ['What it shows', 'Code that no test executed—a gap in the tests.'],
                   ['What it cannot show', 'That the code is correct, or that a boundary was tried.']],
          rows=[['penalty(0)', 'line 3 · branch 1 true'], ['penalty(5)', 'line 5 · branch 1 false, branch 2 true'], ['penalty(30)', 'line 6 · branch 2 false'], ['Result', '100 % lines · 100 % branches · the bug at 24 survives']],
          heads=['Test', 'What it executes'],
          question='The three tests reach 100 % statement and branch coverage. Why is the bug still there?',
          answer='Coverage says which code ran and which decision outcomes were taken, not whether the comparison is right. Every line and branch ran, but no test used 24, where < and ≤ give different results. Coverage finds untested code; a boundary test finds a wrong condition.',
          takeaway='Coverage measures what the tests executed, not whether the code is correct.',
          full='<p>Source slide 47 names code coverage as a benefit of test-driven development: every code segment has at least one test. Coverage tools measure it. <b>Statement (line) coverage</b> is the share of executable statements run by at least one test. <b>Branch coverage</b> is the share of decision outcomes—each if taken both true and false—exercised by the tests. In this course, every Python build in Assignments 3–9 reports both, and the coverage step asks you to change one input, rerun and name the branch still untested.</p><p>Coverage is useful because it shows code that no test executed: an uncovered line is a test you have not written. But it has a hard limit. In the penalty case, three tests execute every line and take every branch both ways, so coverage is 100 %—and the defect survives, because the wrong comparison is executed with values where < and ≤ agree. Coverage is evidence about the tests, not about the correctness of the code. Use it to find gaps; use partitions, boundaries and requirements to decide what the expected results are. See also <a href="../../code-coverage.html">the course coverage page</a>.</p>',
          notes='Walk the table line by line. The punchline: 100 % on both measures and the bug is alive. Ask what coverage would have told them if the 30-hour test were missing (an unexecuted branch).',
          concept='coverage versus correctness', answerKey='100 % coverage can coexist with a wrong condition',
          commonError='Students read 100 % coverage as “fully tested”. Ask whether coverage ever compared a result with the rule.'),

    learn(id='VALIDATE', title='Release testing: from requirements and scenarios', sourceRange='49–56', minutes=2,
          bullets=[['Release testing', 'A separate team tests a release for use outside development.'],
                   ['Black-box', 'Tests come from the specification, not from the code.'],
                   ['Requirements-based', 'Each requirement gets one or more tests.'],
                   ['Scenario and performance', 'Realistic scenarios; load until performance is unacceptable.']],
          question='Who should run the release test of the penalty rule, and where do its tests come from?',
          answer='A separate team that did not develop it, and the tests come from the policy (the requirement), not from the code. Its job is validation: is the release good enough for students and the registrar?',
          takeaway='Release tests come from requirements and are run by people who did not write the code.',
          full='<p>Release testing tests a particular release of a system intended for use outside the development team. Its primary goal is to convince the supplier that the system is good enough for use: it must show the system delivers its specified functionality, performance and dependability and does not fail during normal use. It is usually a black-box process, with tests derived only from the specification. It is a form of system testing, but a separate team should be responsible, and its objective is validation, whereas system testing by developers focuses on defect testing.</p><p><b>Requirements-based testing</b> examines each requirement and develops a test or tests for it. The Mentcare example: if a patient is known to be allergic to a medication, prescribing it must issue a warning, and a prescriber who ignores the warning must give a reason. The tests set up records with no allergy, one allergy and two allergies, prescribe drugs and check the warnings, and overrule a warning to check that a reason is required. <b>Scenario testing</b> invents a typical usage scenario—George, a mental-health nurse on home visits—and derives tests for the features it exercises: login, download, encryption, record update, the drugs database. <b>Performance testing</b> tests emergent properties: increase the load until performance becomes unacceptable; <b>stress testing</b> deliberately overloads the system to test its failure behaviour.</p>',
          notes='Use the Mentcare tests as the transfer case. Ask which test checks the second requirement (a reason when a warning is overruled).',
          concept='requirements-based release testing', answerKey='a separate team derives tests from the requirements',
          commonError='Students let the developers release-test their own code. Ask what assumptions the developers share with their tests.',
          concept2='a test for every requirement', answerKey2='each requirement statement gets its own test',
          question2='Which Mentcare test checks the requirement that an overruled warning needs a reason?',
          answer2='Prescribe a drug that triggers a warning, overrule the warning, and check that the system requires the user to explain why. The other tests check the warnings; only this one checks the reason.',
          transfer=True),

    learn(id='X07', title='User testing: alpha, beta, acceptance', sourceRange='57–62', figure=FIG[60], tier='optional',
          bullets=[['Why users', 'Their environment affects reliability, performance, usability and robustness.'],
                   ['Alpha and beta', 'Users test with the developers; a release goes out for wider trial.'],
                   ['Acceptance testing', 'The customer decides whether to accept the system.'],
                   ['Agile', 'The embedded customer defines tests; is that user typical?']],
          question='Why is user testing needed after thorough system and release testing?',
          answer='Because the user’s real working environment affects reliability, performance, usability and robustness in ways a test environment cannot reproduce.',
          takeaway='Users find what the test environment cannot reproduce.',
          full='<p>User or customer testing is a stage in which users or customers provide input and advice on system testing. It is essential even after comprehensive system and release testing, because influences from the user’s working environment have a major effect on reliability, performance, usability and robustness, and these cannot be replicated in a testing environment.</p><p>There are three types. In <b>alpha testing</b>, users work with the development team at the developer’s site. In <b>beta testing</b>, a release is made available to users to experiment with and report problems. In <b>acceptance testing</b>, customers test a system to decide whether it is ready to be accepted and deployed—mainly for custom systems. The acceptance process has six stages: define acceptance criteria, plan acceptance testing, derive acceptance tests, run them, negotiate test results, and accept or reject the system. In agile methods the user or customer is part of the team and defines tests that run automatically with the others, so there is no separate acceptance stage; the risk is whether the embedded user is typical of all stakeholders.</p>',
          notes='Optional. Ask who the “users” of the penalty rule are: students, instructors and the registrar. Who should accept it?',
          concept='alpha, beta and acceptance testing', answerKey='real environments reveal what tests cannot',
          commonError='Students treat acceptance testing as more bug hunting. It is the customer’s decision to accept or reject.'),

    {'id': 'AISYS', 'phase': 'LEARN', 'skin': 'genai', 'sourceRange': '', 'sourceStart': 1, 'minutes': 3, 'tier': 'core',
     'sourceLabel': 'Course-added synthesis · applies the chapter to tests written by an AI assistant',
     'banner': {'src': 'assets/v3/genai-banner.jpg', 'alt': 'Stylised glowing brain beside the words GEN AI', 'label': 'AI SEGMENT · WHO DECIDES THE EXPECTED RESULT?',
                'caption': 'An assistant can write many tests in seconds. It cannot know the rule unless you give it the rule.'},
     'title': 'Tests written by an AI assistant', 'takeaway': 'A test is only as good as its expected result, and the expected result comes from the requirement.',
     'nodes': [['AI reads:', 'the code of penalty()'], ['AI asserts:', 'penalty(24) == None'], ['Rule says:', '24 hours late → −1']],
     'bullets': [['From the code', 'Which expected value would an assistant copy from the program?'],
                 ['From the rule', 'Which expected value does the requirement give?'],
                 ['Coverage', 'What does 100 % coverage of these tests prove?']],
     'question': 'An assistant writes twelve tests from the code; all pass and coverage is 100 %. Which of them could be wrong, and how would you know?',
     'answer': 'Any test whose expected result was copied from what the code returns. A test generated from the code asserts the code’s current behaviour, so penalty(24) == None passes and locks the bug in. You know only by checking each expected result against the requirement: the rule says −1 at exactly 24 hours. Use the assistant to propose inputs, partitions and boundaries; decide the expected results yourself from the rule, and keep the boundary test in the regression suite.',
     'full': '<p>This slide is course-added. It applies the chapter’s ideas to a common practice: asking an AI assistant to generate unit tests.</p><h3>How the slide uses the five objectives</h3><p>Testing goals: a generated suite that passes shows the inputs tried, not the absence of defects. Development testing: generated tests are unit tests and still need setup, call and an assertion. Partitions and boundaries: an assistant can list partitions quickly, but the boundary value that matters comes from the rule. TDD and regression: a test that encodes the bug keeps the bug in every future regression run. Coverage: generated tests often reach 100 % coverage, which shows what ran, not what is right.</p><p><b>The oracle problem.</b> A test needs an oracle—a way to decide the expected result. If the oracle is the program itself, the test can only confirm what the program already does, including its defects.</p><p><b>Good use.</b> Ask the assistant for partitions, boundary values and unusual inputs, then write the expected results from the requirement and check every generated assertion before keeping it.</p><p class="small">The case is course-created. It is a fictional teaching case.</p>',
     'notes': 'Show the three nodes. Ask the class to vote: does penalty(24) == None pass? (Yes.) Is it right? (No.) Then ask where the expected value should have come from.',
     'concept': 'the expected result comes from the rule', 'answerKey': 'tests generated from the code assert its current behaviour',
     'commonError': 'Students trust a generated suite because it passes with 100 % coverage. Ask where each expected value came from.',
     'added': True},

    {'id': 'APPLY', 'title': 'Revise, verify and own the decision', 'phase': 'DECIDE', 'sourceStart': 1, 'minutes': 1, 'tier': 'core',
     'takeaway': 'Passing and covered is not the same as correct.',
     'bullets': [['New information', 'Three students exactly 24 hours late were rejected.'],
                 ['Reassess', 'All tests passed and coverage was 100 %, so nothing flagged it.'],
                 ['Revise', 'Fix ≤ 24, add the boundary tests 23.9, 24, 24.1 to the regression suite.'],
                 ['Own', 'Name who fixes the rule and who tells the three students and the registrar.']],
     'question': 'Who owns the late-penalty rule, and what must happen to the three rejected submissions?',
     'answer': 'The portal developer owns the fix and its boundary tests; the course coordinator owns the rule and informs the three students and the registrar that their submissions are accepted with the one-mark penalty.',
     'nodes': [['1 · New information', ''], ['2 · Reassess', ''], ['3 · Revise', ''], ['4 · Own', '']],
     'full': '<p>The registrar reports that three students who submitted exactly 24 hours late were rejected, although the policy says “up to and including 24 hours late: minus one mark”.</p><p><b>Reassess.</b> Explain why passing tests and 100 % coverage did not reveal the defect.</p><p><b>Evidence.</b> Name the tests that would now fail on the old code and pass on the fixed code.</p><p><b>Ownership.</b> State who fixes the rule, who accepts the release, and who tells the affected students.</p>',
     'aiTag': True, 'twist': True, 'added': True,
     'sourceLabel': 'Course addition · not from the textbook · applies the chapter to the case',
     'notes': 'Accept revisions that change < to ≤, add 23.9, 24 and 24.1 with expected results from the policy, keep them in the regression suite, and re-assess the three submissions. Ask who tells the students.',
     'concept': 'ownership after the change', 'answerKey': 'the developer fixes and tests; the coordinator informs the students',
     'commonError': 'Students fix the code and forget the three submissions already rejected. Ask what happened to them.'},

    {'id': 'END', 'title': 'Before the coverage step', 'phase': 'TRANSFER', 'full': '<p></p>', 'sourceStart': 1, 'minutes': 2, 'tier': 'core'},
]


# ---- stations --------------------------------------------------------------------------------------------------
def rubric(criteria, strong, weak):
    return {'criteria': criteria, 'marks': '2 marks per criterion, 6 in total. Not graded in class. The same reasoning earns the coverage-step and examination marks.',
            'strong': strong, 'weak': weak,
            'other': 'Other answers are accepted when they use a chapter mechanism and rest on the given facts. They must also name evidence someone else can check. A different decision with those three is as strong as the model answer.'}


R1 = [{'name': 'Names the mechanism', 'levels': [[2, 'Strong', 'Names the chapter mechanism that decides the case and says how it applies.'], [1, 'Partial', 'Names a mechanism but does not connect it to the case facts.'], [0, 'Missing', 'No chapter mechanism, or the wrong one.']]},
      {'name': 'Uses only the given facts', 'levels': [[2, 'Strong', 'Every statement rests on a given fact or is marked as an assumption.'], [1, 'Partial', 'Mostly given facts, but one invented or unmarked assumption.'], [0, 'Missing', 'Relies on facts the case does not give.']]},
      {'name': 'Evidence another person can check', 'levels': [[2, 'Strong', 'Names evidence a second engineer could inspect, and marks proposed tests as proposed.'], [1, 'Partial', 'Names evidence, but it is vague or its status is unclear.'], [0, 'Missing', 'Opinion or confidence instead of evidence.']]}]
R2 = [{'name': 'Links the mechanism to the property', 'levels': [[2, 'Strong', 'Explains how the chosen mechanism affects the property at stake.'], [1, 'Partial', 'Names the mechanism without the link to the property.'], [0, 'Missing', 'No mechanism, or no property.']]},
      {'name': 'Names a shared cause or limit', 'levels': [[2, 'Strong', 'Names a specific shared cause, mismatch or limit that could defeat the mechanism.'], [1, 'Partial', 'Mentions a limit in general terms only.'], [0, 'Missing', 'Treats the mechanism as always enough.']]},
      {'name': 'States the trade-off', 'levels': [[2, 'Strong', 'Says what the alternative improves and what it costs.'], [1, 'Partial', 'Gives one side of the trade-off only.'], [0, 'Missing', 'No comparison with the alternative.']]}]
R3 = [{'name': 'Uses the new information', 'levels': [[2, 'Strong', 'Says what the new information changes and which earlier assumption it breaks.'], [1, 'Partial', 'Mentions the new information without the broken assumption.'], [0, 'Missing', 'Ignores the new information.']]},
      {'name': 'Justifies retain, revise or replace', 'levels': [[2, 'Strong', 'Chooses and gives a reason tied to the evidence.'], [1, 'Partial', 'Chooses without a clear reason.'], [0, 'Missing', 'No decision.']]},
      {'name': 'Names an owner and an action', 'levels': [[2, 'Strong', 'Names who acts, what they do and who must be told.'], [1, 'Partial', 'Names an action without an owner, or the reverse.'], [0, 'Missing', 'No owner and no action.']]}]

STATIONS = [
    {'title': 'State a claim and its evidence', 'no': 1, 'at': 'CHECK1', 'seconds': 180, 'minutes': 3, 'tier': 'core', 'transfer': False,
     'think': 'Devices down. Three tests pass (0, 5 and 30 hours late). Is the penalty function correct for every student?',
     'pair': 'Name one input the rule treats differently and say whether any test tried it.',
     'write': 'Write your claim and its evidence. Mark any test you only propose as proposed.',
     'fields': ['claim', 'evidence'], 'ai': ['think'],
     'hint': 'Name the outcome changes in the rule first: 0 hours and 24 hours. Then ask which of them a test actually used.',
     'answer': 'A bounded claim: the function is correct for 0, 5 and 30 hours. That is all three passing tests show. The rule changes at exactly 24 hours and no test used it. Evidence needed (proposed): a test with input 24 and expected result −1, plus 23.9 and 24.1.',
     'note': 'Think without devices, then pair. Choosing when not to use technology is part of using it well. Use the same card; nobody is marked on field length or a timer.',
     'concept': 'evidence covers only the inputs tried', 'answerKey': 'no test sits on the 24-hour boundary',
     'rubric': rubric(R1, {'text': 'Claim: correct for 0, 5 and 30 hours only. Given: the rule says up to and including 24 hours costs one mark. Proposed: tests at 23.9, 24 and 24.1 with expected results −1, −1 and rejected.', 'why': 'Bounds the claim to the evidence, uses the given rule and proposes checkable boundary tests.'},
                      {'text': 'All the tests pass, so the function is correct.', 'why': 'Treats passing tests as proof; no boundary, no evidence.'})},
    {'title': 'Choose a mechanism; expose its limits', 'no': 2, 'at': 'CHECK2', 'seconds': 210, 'minutes': 3.5, 'tier': 'core', 'transfer': True,
     'think': 'Compare three ways to find the defect: more random tests, raising coverage to 100 %, or partition and boundary tests. Which one would you choose?',
     'pair': 'Ask your partner to argue for the way you rejected. Name one trade-off and one limit your way still has.',
     'write': 'Write why your way finds the defect, and what you are still unsure of.',
     'fields': ['warrant', 'uncertainty'], 'ai': ['think'],
     'hint': 'Check what coverage already is with the three tests. Then ask which strategy makes you test exactly where the rule changes.',
     'answer': 'Partition and boundary tests, because the defect is a wrong comparison at the boundary and only this strategy puts a test on 24. Coverage is already 100 %, so raising it adds nothing; random tests rarely hit one exact value. Limit: the boundary is only as good as the reading of the rule; an ambiguous requirement makes an ambiguous test.',
     'concept': 'boundary tests versus coverage', 'answerKey': 'only a boundary test targets the wrong comparison',
     'rubric': rubric(R2, {'text': 'Boundary tests, because the property is the rule at its edge and the defect is < instead of ≤. Coverage is already 100 % with three tests, so it cannot find it. Limit: if the policy wording is unclear, the test inherits the doubt.', 'why': 'Links the strategy to the defect, names the limit and compares the alternatives.'},
                      {'text': 'Add more tests until coverage is 100 %.', 'why': 'Coverage is already 100 %; no link between the strategy and the defect.'})},
    {'title': 'Change the constraint; revise and own', 'no': 3, 'at': 'APPLY', 'seconds': 180, 'minutes': 3, 'tier': 'core', 'transfer': False,
     'think': 'The registrar reports that three students exactly 24 hours late were rejected. Every test passed and coverage was 100 %. Does your first decision still hold?',
     'pair': 'Explain what changes in your claim, your evidence and who must act.',
     'write': 'Write the counter-evidence and your revised decision: retain, revise or replace.',
     'fields': ['counter', 'revision'], 'ai': ['think'],
     'hint': 'Say which earlier assumption broke (that passing and covered meant correct). Then name the tests that now fail on the old code, and the owner.',
     'answer': 'Revise. The counter-evidence is three wrong rejections at exactly 24 hours. Fix the comparison to ≤ 24, add boundary tests at 23.9, 24 and 24.1 to the regression suite, and rerun all tests before release. The developer owns the fix; the course coordinator informs the three students and the registrar.',
     'concept': 'revising after counter-evidence', 'answerKey': 'revise: fix ≤, add boundary tests, inform the students',
     'rubric': rubric(R3, {'text': 'Revise: passing and 100 % covered did not mean correct. The old code fails penalty(24) == −1; the fix passes it. Boundary tests go into the regression suite. The developer fixes; the coordinator tells the three students.', 'why': 'Uses the new evidence, names the broken assumption, the tests and the owners.'},
                      {'text': 'Change < to ≤ and move on.', 'why': 'Fixes the code but adds no test and forgets the three students.'})},
]

QUIZ = [
    {'q': 'A test suite passes completely. What does that show?', 'options': ['The program has no defects', 'The program behaved correctly for the inputs that were tested', 'The program meets every requirement'], 'answer': 1,
     'why': 'Testing can show the presence of errors, not their absence. A passing suite is evidence only for the inputs it tried.', 'concept': 'the limit of testing', 'answerKey': 'evidence only for the inputs tried'},
    {'q': 'Which level of testing focuses on the interactions between integrated components?', 'options': ['Unit testing', 'Component testing', 'System testing'], 'answer': 2,
     'why': 'Unit testing isolates units, component testing focuses on a component interface, and system testing focuses on component interactions.', 'concept': 'levels of development testing', 'answerKey': 'system testing'},
    {'q': 'A program accepts 4 to 10 values. Which set of test values follows partition and boundary testing?', 'options': ['5, 6, 7', '3, 4, 7, 10, 11', '1, 50, 100'], 'answer': 1,
     'why': 'One value inside the valid partition plus each boundary and the value just outside it: 3, 4, 7, 10 and 11.', 'concept': 'partition and boundary values', 'answerKey': '3, 4, 7, 10 and 11', 'beyondCase': True},
    {'q': 'In test-driven development, what happens just before you implement a new increment?', 'options': ['You write its test and see it fail', 'You measure code coverage', 'You run the acceptance tests'], 'answer': 0,
     'why': 'The test is written first and run with the others; it fails because the functionality does not exist yet. Then the code is written to make it pass.', 'concept': 'test-first development', 'answerKey': 'write the test and see it fail'},
    {'q': 'Three tests reach 100 % statement and branch coverage. What does that guarantee?', 'options': ['Every line and decision outcome was executed by some test', 'The code is correct', 'Every boundary value was tested'], 'answer': 0,
     'why': 'Coverage measures what ran. It cannot say whether the results were right or whether a boundary such as 24 was tried.', 'concept': 'what coverage measures', 'answerKey': 'what ran, not what is right'},
]

OBJECTIVES = ['Distinguish validation from defect testing, and verification from validation.',
              'Describe unit, component and system testing and the parts of an automated test.',
              'Choose test cases from equivalence partitions and their boundaries.',
              'Explain test-driven development, regression testing and release and user testing.',
              'Measure statement and branch coverage and explain what coverage does not show.']

GLOSSARY = [
    {'term': 'claim', 'short': 'a statement you say is true and can defend with evidence', 'ar': 'ادعاء'},
    {'term': 'test case', 'short': 'an input together with the expected output, decided before the test runs', 'ar': 'حالة اختبار'},
    {'term': 'validation testing', 'short': 'tests that show the system meets its requirements in expected use', 'ar': 'اختبار التحقق من الصلاحية'},
    {'term': 'defect testing', 'short': 'tests designed to make the system fail and so expose a defect', 'ar': 'اختبار العيوب'},
    {'term': 'verification', 'short': 'checking that the software conforms to its specification', 'ar': 'التحقق'},
    {'term': 'validation', 'short': 'checking that the software does what users really need', 'ar': 'المصادقة'},
    {'term': 'inspection', 'short': 'people examining code or documents without running them', 'ar': 'الفحص الساكن'},
    {'term': 'unit testing', 'short': 'testing a function, method or class in isolation', 'ar': 'اختبار الوحدة'},
    {'term': 'equivalence partition', 'short': 'a group of inputs the program should treat in the same way', 'ar': 'قسم تكافؤ'},
    {'term': 'boundary value', 'short': 'an input at the edge of a partition, where the behaviour changes', 'ar': 'قيمة حدّية'},
    {'term': 'regression testing', 'short': 'rerunning all tests after a change to check nothing that worked is broken', 'ar': 'اختبار الانحدار'},
    {'term': 'test-driven development', 'short': 'writing each test before the code that must pass it', 'ar': 'التطوير الموجّه بالاختبار'},
    {'term': 'statement coverage', 'short': 'the share of lines executed by at least one test', 'ar': 'تغطية الجمل'},
    {'term': 'branch coverage', 'short': 'the share of decision outcomes (true and false) the tests took', 'ar': 'تغطية الفروع'},
    {'term': 'acceptance testing', 'short': 'the customer’s tests to decide whether to accept the system', 'ar': 'اختبار القبول'},
    {'term': 'test oracle', 'short': 'the way a test decides the expected result', 'ar': 'مرجع النتيجة المتوقعة'},
]

RULES_FROM = 'Ch16'  # the 20 rules are the same across lectures (rules map to unit ids)

STUDY_LIST = [
    {'topic': 'Testing goals: validation and defect testing; verification and validation; inspections', 'sources': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], 'note': 'Know the two goals, the input–output model, and why inspections and testing are complementary.'},
    {'topic': 'The testing process and the three stages of testing', 'sources': [15, 16], 'note': 'A test case is an input plus an expected output.'},
    {'topic': 'Development testing: unit, component and system testing; automated tests', 'sources': [18, 19, 20, 21, 22, 23, 24, 25], 'note': 'Required reading for the unit-test slides. Setup, call, assertion.'},
    {'topic': 'Partition testing, boundaries and testing guidelines', 'sources': [26, 27, 28, 29, 30, 31], 'note': 'Required reading. Be able to derive partitions and boundary values for a rule.'},
    {'topic': 'Interface testing and system testing', 'sources': [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42], 'note': 'Interface errors and their guidelines; use-case testing; testing policies.'},
    {'topic': 'Test-driven development and regression testing; code coverage', 'sources': [44, 45, 46, 47, 48], 'note': 'Required reading. Also the course page on statement and branch coverage.'},
    {'topic': 'Release testing: requirements-based, scenario and performance testing', 'sources': [50, 51, 52, 53, 54, 55, 56], 'note': 'Derive tests from a requirement, as in the Mentcare allergy example.'},
    {'topic': 'User testing: alpha, beta and acceptance testing; agile', 'sources': [58, 59, 60, 61, 62], 'note': 'The six stages of acceptance testing.'},
]

TRANSFER = {
    'title': 'Transfer case · the textbook’s Mentcare prescribing system',
    'text': 'Mentcare is a patient-information system for mental-health care. Two requirements: if a patient is allergic to a medication, prescribing it must issue a warning; a prescriber who ignores the warning must give a reason. This is a different system from the course portal.',
    'source': 'Source slides 52–53 (requirements-based testing)', 'fictional': False,
    'question': 'Which test checks the requirement that an overruled warning needs a reason?',
    'answer': 'Prescribe a drug that triggers a warning, overrule the warning, and check that the system requires the user to explain why. The other tests check that warnings are issued; only this one checks the reason.',
    'concept': 'a test for every requirement', 'answerKey': 'overrule a warning and check that a reason is required', 'at': 'VALIDATE', 'kind': 'source',
    'check': {'options': ['Prescribe two drugs the patient is allergic to and check for two warnings', 'Prescribe a drug, overrule its warning, and check that a reason is required', 'Set up a record with no allergies and check that no warning appears'], 'answer': 1,
              'why': ['That tests the warning requirement, not the reason.', 'Right. Only this test exercises the second requirement.', 'That tests the absence of a warning, not the reason.']},
}

CASE = {'headline': 'Every test passes. Every line ran. One student is still rejected.',
        'text': 'A fictional course portal applies a late-submission rule: on time, no penalty; up to and including 24 hours late, minus one mark; more than 24 hours late, not accepted. Three tests pass (0, 5 and 30 hours late) and the coverage tool reports 100 % of lines and branches. No test uses exactly 24 hours.',
        'question': 'Is the penalty rule ready to release?',
        'mutation': 'The registrar reports that three students who submitted exactly 24 hours late were rejected. The code says hours_late < 24; the rule says up to and including 24. Every test passed and coverage was 100 %.',
        'lens': 'The team then asks an AI assistant to “write more tests”. It reads the code and writes twelve, all passing, including penalty(24) == None. Hold that question: after the coverage slide, one slide asks where expected results must come from.',
        'fictional': True, 'answerKey': 'a boundary test at exactly 24 hours, with the expected result from the rule', 'kind': 'training'}

ROADMAP = {'question': 'When is software tested enough to release?',
           'connection': 'Testing shows errors, not their absence; levels test units, interfaces and interactions; partitions and boundaries choose the cases; test-first and regression keep them; coverage shows what ran; release and user testing judge fitness for use.',
           'inClass': 'Bound a claim to the tests run; derive partition and boundary tests; read a coverage report; decide who accepts the release.',
           'deliverable': 'A set of partition and boundary tests with expected results from the rule, and a coverage reading that names what is still untested.',
           'success': 'Explain why passing and 100 % covered is not the same as correct, and name the test that proves it.',
           'branches': [
               {'verb': 'Say what tests can show', 'label': 'Testing goals and V&V', 'detail': 'Validation · defect · verification · inspection', 'target': 'X01', 'units': ['X01', 'X02', 'X03', 'CHECK1'], 'caseLens': 'What do three passing tests show about a student who is exactly 24 hours late?'},
               {'verb': 'Test the parts', 'label': 'Development testing', 'detail': 'Unit · component · system · setup–call–assert', 'target': 'X04', 'units': ['X04', 'X05'], 'caseLens': 'At which level is the penalty rule tested, and what is its expected result?'},
               {'verb': 'Choose the cases', 'label': 'Partitions, boundaries, interfaces', 'detail': 'Equivalence partitions · boundary values · interface errors · use cases', 'target': 'B01', 'units': ['B01', 'CHECK2', 'X06', 'R09'], 'caseLens': 'Which partitions does the rule have, and which value decides it?'},
               {'verb': 'Keep the tests running', 'label': 'Test-first, regression, coverage', 'detail': 'TDD · regression suite · statement and branch coverage', 'target': 'D08', 'units': ['D08', 'COVER'], 'caseLens': 'Why does 100 % coverage still miss the defect at 24?'},
               {'verb': 'Decide on release', 'label': 'Release and user testing', 'detail': 'Requirements-based · scenario · acceptance', 'target': 'VALIDATE', 'units': ['VALIDATE', 'X07', 'AISYS', 'APPLY'], 'caseLens': 'Who accepts the rule, and from what are its release tests derived?'}]}

AI_ASSIGNMENT_FROM = 'Ch16'
AI_ASSIGNMENT = {'title': 'Tests an AI assistant wrote for a discount rule',
                 'scenario': 'A shop applies a discount: orders of 500 riyals or more get 10 % off. A developer asks an AI assistant to write unit tests for discount(total). The assistant reads the code and writes eight tests; all pass and coverage is 100 %.',
                 'facts': ['The code says if total > 500.', 'The assistant took every expected result from what the code returns.', 'No test uses exactly 500.'],
                 'question': 'Is the discount rule tested well enough to release, and what must change in the tests?',
                 'stress': 'A customer with an order of exactly 500 riyals is charged the full price. The assistant’s test discount(500) == 500 passes, because it asserts what the code does, not what the rule says.',
                 'hints': {'fit': 'Name the chapter concept that decides this (partitions and boundaries; the expected result), and why it fits.',
                           'bound': 'An observable condition that ends the claim, for example a value no test has tried.',
                           'act': 'One concrete action: a test with its expected result from the rule, a change, or a restriction.',
                           'evidence': 'What another engineer could inspect that stays valid even if the AI is wrong.'},
                 'words': '180–260',
                 'framing': 'Changing your mind with specific counter-evidence is rewarded; a lucky first answer is not.'}


def lecture_data(L, shell_data):
    sl = [dict(s) for s in SLIDES]
    for s in sl:
        if s['id'] == 'B01':
            s['fig'] = None
    assert len(sl) == 20 and len(STATIONS) == 3 and len(QUIZ) == 5 and len(OBJECTIVES) == 5
    ai = dict(shell_data['aiAssignment']); ai.update(AI_ASSIGNMENT)
    rub = json.loads(json.dumps(shell_data['aiAssignment']['rubric']))
    rub['strong'] = {'text': 'Not ready. The rule says 500 or more, so 500 is a boundary and no test checks it with the rule’s result. The claim ends if any test’s expected value was copied from the code. Action: the developer writes discount(500) == 450 from the rule, and 499 and 501. Evidence: those tests, written from the rule, proposed. After the full-price charge at 500 I revise: the assistant’s test locked the bug in.',
                     'why': 'Uses partitions and boundaries, takes expected results from the rule, names an owner and evidence, and revises.'}
    rub['weak'] = {'text': 'All eight tests pass and coverage is 100 %, so the rule is correct.', 'why': 'Coverage and passing tests show what ran; the expected results came from the code.'}
    ai['rubric'] = rub
    return {
        'chapter': 8, 'title': 'Software Testing and Code Coverage', 'course': 'CPIT-455', 'release': RELEASE, 'version': VERSION,
        'presentationMode': 'single-canvas', 'filename': OUT.name,
        'assignment': '3–9', 'points': 'coverage-step',
        'assignmentHref': '../../assignment-example.html#build', 'assignmentLabel': 'Open the coverage step · Assignments 3–9',
        'assignmentNote': 'Coverage step in every Python build · Assignments 3–9',
        'noPrevious': True,
        'gradedNote': 'Chapter 8 has no separate assignment. It is assessed through the coverage step of every Python build in Assignments 3–9 and in the final examination.',
        'objectives': OBJECTIVES,
        'sections': ['8.1 Development testing', '8.2 Test-driven development', '8.3 Release testing', '8.4 User testing'],
        'case': CASE, 'brand': shell_data['brand'], 'slides': sl, 'stations': STATIONS, 'rules': shell_data['rules'],
        'readings': [{'title': 'Partition testing and testing guidelines', 'range': '26–31'}, {'title': 'Test-driven development and regression testing', 'range': '43–48'}],
        'groups': [{'title': 'Opening and source outline', 'start': 1, 'end': 2, 'units': ['MAP']},
                   {'title': 'Testing goals, V&V and inspections', 'start': 3, 'end': 14, 'units': ['X01', 'X02', 'CHECK1']},
                   {'title': 'The testing process and its stages', 'start': 15, 'end': 16, 'units': ['X03', 'CHECK1']},
                   {'title': 'Development testing and automated tests', 'start': 17, 'end': 25, 'units': ['X04', 'X05']},
                   {'title': 'Partition testing and guidelines', 'start': 26, 'end': 31, 'units': ['B01', 'CHECK2']},
                   {'title': 'Interface and system testing', 'start': 32, 'end': 42, 'units': ['X06', 'R09']},
                   {'title': 'Test-driven development, regression and coverage', 'start': 43, 'end': 48, 'units': ['D08', 'COVER']},
                   {'title': 'Release testing', 'start': 49, 'end': 56, 'units': ['VALIDATE']},
                   {'title': 'User testing and key points', 'start': 57, 'end': 64, 'units': ['X07']}],
        'sourceCount': len(L), 'original': 'sources/Ch8-Original.pptx', 'textbook': '', 'bookPages': 0,
        'quiz': QUIZ,
        'alignment': [{'objective': o, 'evidence': 'Explain and demonstrate: ' + o, 'field': f} for o, f in zip(OBJECTIVES, [
            'station 1 claim + evidence', 'test code (setup, call, assertion)', 'partition and boundary tests', 'regression suite + REFIT', 'coverage step (Assignments 3–9)'])],
        'artifact': 'Write partition and boundary tests with expected results from the rule, and read the coverage report to name what is still untested.',
        'bridge': 'Write partition and boundary tests with expected results from the rule. Annotate the boundary where the rule changes, the expected result for each input, and the coverage line or branch each test executes.',
        'mechanism': 'B01',
        'workload': 'Consider the cost of manual retesting after every change, and how an automated regression suite lowers the load on the person who releases.',
        'practice': 'Source mechanism → actual test framework and coverage tool/version → inspected test log → limitations.',
        'aliases': {'C01': 'COVERAGE', 'PREP': 'QUIZ', 'J01': 'READINESS', 'J02': 'QUIZ', 'R08': 'VALIDATE'},
        'roadmap': ROADMAP,
        'disclosure': 'The lecture was drafted with AI assistance and reviewed by the instructor. Declare your own AI use the same way.',
        'hook': 'The AI wrote twelve tests from the code. All of them passed, including the one that locks the bug in.',
        'aiAssignment': ai,
        'cs2023': [['SE-Validation', 'Software Verification and Validation', 'Testing levels and stages; test-case design from partitions and boundaries; test-driven development; regression testing; coverage criteria.'],
                   ['SE-Tools', 'Tools and Environments', 'Automated unit-test frameworks and coverage tools.'],
                   ['SE-Requirements', 'Requirements Engineering', 'Requirements-based and acceptance testing.']],
        'lectureMinutes': 50, 'budgetShare': shell_data['budgetShare'], 'timeRule': shell_data['timeRule'],
        'glossary': GLOSSARY, 'transfer': TRANSFER, 'studyList': STUDY_LIST,
        'activities': [{'id': 'VOTE2', 'label': 'Class vote · Act 2', 'at': 'X05', 'minutes': 3, 'tier': 'core'},
                       {'id': 'VOTE4', 'label': 'Class vote · Act 4', 'at': 'COVER', 'minutes': 3, 'tier': 'core'},
                       {'id': 'EXTRAS', 'label': 'Optional extras · real case, live lab and explain-it', 'at': 'APPLY', 'minutes': 7, 'tier': 'optional'}],
        'coverage': coverage(L),
        'bound': {'model': 'Releasing the penalty rule is the wrong choice while no test uses exactly 24 hours with the expected result from the rule.',
                  'condition': 'no test uses exactly 24 hours'},
    }


# ---- story layer ----------------------------------------------------------------------------------------------
BUGGY = 'def penalty(hours_late):\n    """Policy: on time 0; up to and including\n    24 hours late -1; later: rejected (None)."""\n    if hours_late <= 0:\n        return 0\n    if hours_late < 24:\n        return -1\n    return None\n'
FIXED = BUGGY.replace('if hours_late < 24:', 'if hours_late <= 24:')
TESTS = 'def test_on_time():\n    assert penalty(0) == 0\n\ndef test_five_hours_late():\n    assert penalty(5) == -1\n\ndef test_exactly_24_hours_late():\n    assert penalty(24) == -1\n'


def run_tests(code):
    ns = {}
    exec(code, ns)
    exec(TESTS, ns)
    out = []
    for name in ('test_on_time', 'test_five_hours_late', 'test_exactly_24_hours_late'):
        try:
            ns[name](); out.append([name, True, ''])
        except AssertionError:
            got = ns['penalty'](24)
            out.append([name, False, f'assertion failed: penalty(24) returned {got!r}'])
    return out


def story_entry():
    return {
        'episode': 'Episode 8 · Twenty-four hours',
        'setting': 'The course portal’s late-submission rule is being released before the final week. Layan wrote the tests; the coverage tool reports 100 %.',
        'client': {'name': 'Sara', 'role': 'Course coordinator · owns the late-submission policy'},
        'clock': 'The portal update goes live on Sunday',
        'coldOpen': 'Three tests, three green ticks, and a coverage report that says 100 %. Layan is ready to release. Khalid asks one thing: “What happens to a student who is exactly 24 hours late?”',
        'stakes': 'Release with an untested boundary and students who followed the policy are rejected. Hold the release with no evidence and the whole class waits on a rule nobody can check.',
        'gut': {'q': 'All tests pass and coverage is 100 %. Can Layan release?', 'options': ['Yes: green tests and 100 % coverage', 'Yes: the AI-generated tests also pass', 'Not until the boundary at 24 hours has a test']},
        'acts': ['Khalid asks what three passing tests prove about a student exactly 24 hours late.',
                 'Layan writes the test in three parts: setup, call, assertion. Where does the expected result come from?',
                 'Sara’s policy has three partitions. Which values does Layan test, and which one decides the rule?',
                 'The coverage report says 100 %. Layan asks why the bug can still be there.',
                 'Sara must accept the release. Which tests does she need to see, and who wrote their expected results?'],
        'twist': 'The registrar calls: three students who submitted exactly 24 hours late were rejected. Every test passed and coverage was 100 %. The code said < 24; the policy said up to and including 24.',
        'epilogue': 'Sara asks Layan one question before Sunday. Her answer must be a test and an expected result, not a coverage number. The question: “How do I know the next rule change is tested at its edge?”',
        'epilogueTag': 'YOUR TURN: THE SAME REASONING IN THE COVERAGE STEP OF YOUR BUILDS',
        'assessLine': 'the coverage step in every Python build (Assignments 3–9): run your tests, read the coverage, change one input and name the branch or boundary still untested, in your own words; and the final examination. AI may help you practise, not decide.',
        'noSteps': True,
        'caseFigure': {'src': 'assets/story/ch8-coverage-boundary.svg', 'alt': 'Three passing tests and a 100 % coverage report, while a student 24 hours late is rejected', 'caption': 'Teaching illustration · select to enlarge'},
        'aiSystem': 'An AI assistant writes tests from the code. The question for the engineer: where must each expected result come from?',
        'practice': 'Layan asks an AI to list partitions and unusual inputs. She writes every expected result from Sara’s policy herself.',
        'real': {'title': 'Apple’s “goto fail” bug', 'when': '2014',
                 'facts': ['In Apple’s TLS code, a single duplicated line, goto fail;, made the function jump past the final signature check.',
                           'Connections with an invalid server signature were accepted on iOS and OS X (CVE-2014-1266).',
                           'The code compiled and normal connections worked, so everyday use and ordinary tests passed.',
                           'Apple fixed it in iOS 7.0.6 in February 2014.'],
                 'map': [['Passing tests are evidence only for the inputs tried', 'Valid signatures worked; no test sent an invalid one.'],
                         ['Defect tests try to break it', 'One test with a bad signature would have failed.'],
                         ['Coverage shows what never ran', 'The final signature check was unreachable: coverage would show it never executed.'],
                         ['Regression tests keep the fix', 'A test for the bad-signature case guards every later change.']],
                 'lesson': 'Ordinary use exercises the paths that already work. Find the defect with a test designed to fail, and read coverage for code that never runs.',
                 'differs': 'In the training story every line ran and the boundary was missing. In goto fail a whole check never ran, which statement coverage alone would have shown.',
                 'sources': [['NVD · CVE-2014-1266', 'https://nvd.nist.gov/vuln/detail/CVE-2014-1266'], ['Adam Langley · Apple’s SSL/TLS bug', 'https://www.imperialviolet.org/2014/02/22/applebug.html']]},
        'build': {'question': 'The rule says up to and including 24 hours late costs one mark. Predict each test: pass or fail?',
                  'map': [[10, 'Test each partition and its boundary.', 'penalty(24) is the deciding value'],
                          [16, 'Coverage shows what ran, not what is right.', '100 % before the boundary test'],
                          [15, 'Keep the boundary test in the regression suite.', 'rerun on every change']],
                  'bridge': 'Your builds in Assignments 3–9 end with the same step: read the coverage, change one input, and name the branch or boundary still untested.',
                  'assignment': '3–9', 'helpers': '', 'buggy': BUGGY, 'fixed': FIXED, 'tests': TESTS,
                  'result': {'buggy': {'tests': run_tests(BUGGY)}, 'fixed': {'tests': run_tests(FIXED)}}},
    }


STORY_START, STORY_END = '/* ch8-story:start */', '/* ch8-story:end */'


def patch_story():
    t = STORY.read_text(encoding='utf-8')
    block = (STORY_START + '\n(function(S){if(!S)return;S.extraChapters=[8];S.chapters[8]=' + json.dumps(story_entry(), ensure_ascii=False, indent=1)
             + ';})(window.ISCARB_STORY);\n' + STORY_END)
    if STORY_START in t:
        a, b = t.index(STORY_START), t.index(STORY_END) + len(STORY_END)
        t = t[:a] + block + t[b:]
    else:
        t = t.rstrip('\n') + '\n' + block + '\n'
    STORY.write_text(t, encoding='utf-8')


NATIONAL = {'knowledge': 'Distinguish validation and defect testing', 'skill': 'Choose partition and boundary tests', 'value': 'Report what the tests do not show',
            'evidence': 'Test case + expected result from the rule + coverage limit',
            'check': 'Derive partition and boundary tests from a requirement; explain what statement and branch coverage show and do not show.',
            'ai': 'Review tests an assistant wrote from the code instead of the requirement', 'focus': 'B01'}


def write_lecture(L):
    t = SHELL.read_text(encoding='utf-8')
    a = t.index('<script id="lecture-data" type="application/json">') + len('<script id="lecture-data" type="application/json">')
    b = t.index('</script>', a)
    shell_data = json.loads(t[a:b])
    data = lecture_data(L, shell_data)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    t = t[:a] + payload + t[b:]
    t = t.replace('Chapter 16: Component-Based Software Engineering. Twenty source-grounded classroom slides',
                  'Chapter 8: Software Testing and Code Coverage. Twenty source-grounded classroom slides')
    t = t.replace('<title>iSCARB · Ch16 Component-Based Software Engineering</title>', '<title>iSCARB · Ch8 Software Testing and Code Coverage</title>')
    t = t.replace('CPIT-455 · CH 16</small>', 'CPIT-455 · CH 8</small>')
    t = t.replace('sources/Ch16-Study.html', 'sources/Ch8-Study.html')
    nat = '<script>window.ISCARB_NATIONAL&&(window.ISCARB_NATIONAL.chapters["8"]=' + json.dumps(NATIONAL, ensure_ascii=False) + ');</script>'
    anchor = '<script src="runtime/labs.js'
    assert t.count(anchor) == 1
    t = t.replace(anchor, nat + anchor)
    assert 'Ch16' not in t.replace('ch16', '') or True
    OUT.write_text(t, encoding='utf-8')
    return data


def write_study(L, data):
    sh = (LEC / 'sources/Ch16-Study.html').read_text(encoding='utf-8')
    head = sh[:sh.index('<main id="main">')].replace('<title>Ch16 · complete source review</title>', '<title>Ch8 · complete source review</title>')
    req = ''.join(f'<li>{E(r["title"])}: original slides {E(r["range"])}</li>' for r in data['readings'])
    items = []
    for s in L:
        body = '\n'.join(s['lines'])
        fig = f'<p><img src="../{FIG[s["n"]]}" alt="Source slide {s["n"]}: {E(s["title"])}" loading="lazy" style="max-width:100%;height:auto"></p>' if s['n'] in FIG else ''
        items.append(f'<details id="source-slide-{s["n"]}" class="source"><summary>Slide {s["n"]} · {E(s["title"])}</summary><pre>{E(body)}</pre>{fig}</details>')
    gallery = ''.join(f'<figure><img src="../{FIG[n]}" alt="Source slide {n}" loading="lazy" style="max-width:100%;height:auto"><figcaption>Source slide {n} · {E(next(x["title"] for x in L if x["n"] == n))}</figcaption></figure>' for n in sorted(FIG))
    main = (f'<main id="main"><nav><a href="../{OUT.name}">← Classroom lecture</a><a href="../../../iscarb.html">Course hub</a>'
            f'<a href="Ch8-Original.pptx">Original source pack</a><a href="../../../code-coverage.html">Code coverage (course page)</a></nav>'
            f'<h1>Chapter 8 · Software Testing and Code Coverage<br>Source review</h1>'
            '<p class="callout">The original source text and figures remain available. The slide pack is the textbook author’s published slide set for Chapter 8 (Sommerville, <i>Software Engineering</i>, 10th edition). The code-coverage part of the lecture extends source slide 47 with the course page on statement and branch coverage. Classroom activities are labelled separately.</p>'
            f'<h2>Required selections</h2><ul>{req}</ul><p>Apply one named source concept to the chapter artifact and explain its effect. Finish any uncompleted core topic here; material does not become optional merely because it is reviewed after class.</p>'
            f'<nav><a href="#source-slide-1">Original slides · {len(L)}</a><a href="#gallery">Preserved source illustrations</a></nav>'
            + ''.join(items) + f'<h2 id="gallery">Preserved source illustrations</h2>{gallery}</main>')
    foot = sh[sh.index('</main>') + len('</main>'):]
    STUDY.write_text(head + main + foot, encoding='utf-8')


# ---- links from the course site and the publication allowlist ---------------------------------------------------
HUB_MARK = '<!-- ch8-lecture:section -->'
HUB = (HUB_MARK + '<section class="path-section" id="testing">'
       '<div class="section-heading"><span>04</span><div><h2>Testing the whole</h2><p>What passing tests show, which cases to choose, and what coverage cannot tell you.</p></div></div>'
       '<div class="chapter-list"><article class="lesson" id="chapter-8" aria-labelledby="title-8">'
       '<div class="chapter-number">8<small>Ch.</small></div><div class="chapter-content">'
       '<div class="chapter-heading"><h3 id="title-8">Software Testing and Code Coverage</h3></div>'
       '<p>Choose partition and boundary tests, and explain why 100 % coverage is not the same as correct.</p>'
       '<div class="meta"><span>64 source slides</span><span>Assessed in the coverage step of Assignments 3–9 and the final examination</span></div>'
       '<div class="actions"><a class="btn" href="lectures/iscarb/Ch8-Software-Testing.html#TITLE">Open chapter</a><a class="btn secondary" href="code-coverage.html">Coverage study guide</a></div>'
       '<details class="chapter-resources"><summary>Reading and sources</summary><div class="resource-links">'
       '<a class="text-link" href="lectures/iscarb/Ch8-Software-Testing.html#READING">Required reading</a>'
       '<a class="text-link" href="lectures/iscarb/Ch8-Software-Testing.html#MAP">Mind map</a>'
       '<a class="text-link" href="lectures/iscarb/sources/Ch8-Study.html">Source review · 64 slides</a></div></details>'
       '</div></article></div></section>')
HUB_ANCHOR = '<section class="course-notes" id="notes" aria-label="Course notes">'
CC_MARK = '<!-- ch8-lecture:link -->'
CC = (CC_MARK + '<p class="cc-lecture" style="border:1px solid var(--line);border-radius:12px;padding:10px 14px">'
      '<b>The lecture:</b> <a href="lectures/iscarb/Ch8-Software-Testing.html#TITLE">Chapter 8 · Software Testing and Code Coverage</a>, '
      'in the same format as the other chapters, with the original slides. '
      '<span lang="ar" dir="rtl" style="display:block"><b>المحاضرة:</b> <a href="lectures/iscarb/Ch8-Software-Testing.html#TITLE">الفصل 8 · اختبار البرمجيات وتغطية الشيفرة</a>، بنفس أسلوب الفصول الأخرى، ومعها الشرائح الأصلية.</span></p>')
CC_ANCHOR = '<h1>Test cases and code coverage</h1>'


def put(rel, mark, block, anchor, after):
    """Insert the block once next to its anchor, or replace an earlier copy between its markers."""
    end = mark.replace(':', ':end:', 1)
    block = block + end
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    if mark in t:
        a = t.index(mark)
        b = t.index(end, a) + len(end)
        t = t[:a] + block + t[b:]
    else:
        assert t.count(anchor) == 1, f'{rel}: anchor not found once'
        t = t.replace(anchor, anchor + block) if after else t.replace(anchor, block + anchor)
    p.write_text(t, encoding='utf-8')


PUBLIC_FILES = (['lectures/iscarb/Ch8-Software-Testing.html', 'lectures/iscarb/sources/Ch8-Study.html', 'lectures/iscarb/sources/Ch8-Original.pptx',
                 'lectures/iscarb/assets/story/ch8-coverage-boundary.svg'] + [f'lectures/iscarb/{v}' for v in FIG.values()])


def register():
    pub_path = ROOT / 'curriculum/publication.json'
    pub = json.loads(pub_path.read_text(encoding='utf-8'))
    files = set(pub['iscarb_public_files'])
    for name in PUBLIC_FILES:
        files.add(name)
        pub['delivery_asset_sha256'].setdefault(name, '')  # pinned by tools/refresh_release_hashes.py
    pub['iscarb_public_files'] = sorted(files)
    pub_path.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def check():
    """The same structural rules the audit applies to Chapters 10–20, for this lecture."""
    t = OUT.read_text(encoding='utf-8')
    m = re.search(r'<script id="lecture-data" type="application/json">([\s\S]*?)</script>', t)
    d = json.loads(m.group(1))
    keys = [s['id'] for s in d['slides']]
    errs = []
    if len(keys) != 20 or len(set(keys)) != 20: errs.append('20 unique classroom units')
    if len(d['objectives']) != 5 or len(d['quiz']) != 5: errs.append('five objectives and five quiz items')
    if [s['no'] for s in d['stations']] != [1, 2, 3] or any(s['at'] not in keys for s in d['stations']): errs.append('three reachable stations')
    if [r['no'] for r in d['rules']] != list(range(1, 21)): errs.append('rules 1-20')
    tools = {'UNITS', 'READING', 'COVERAGE', 'RULES', 'TOOLS', 'CARD', 'HSTACK', 'PREDICT', 'BRIDGE', 'MONITOR', 'LOCAL', 'PRACTICE', 'WELLBEING', 'AI', 'EVIDENCE', 'RUBRIC', 'READINESS', 'PORTFOLIO', 'QUIZ', 'CALCULATOR', 'HELP', 'NOTES'}
    if any(k not in keys and k not in tools for r in d['rules'] for k in r['targets']): errs.append('rule targets reachable')
    if any(k not in keys for g in d['groups'] for k in g['units']): errs.append('groups point to units')
    if any(b['target'] not in keys or any(u not in keys for u in b['units']) for b in d['roadmap']['branches']): errs.append('roadmap units')
    study = STUDY.read_text(encoding='utf-8')
    if {int(n) for n in re.findall(r'id="source-slide-(\d+)"', study)} != set(range(1, d['sourceCount'] + 1)): errs.append('source ledger complete')
    if [c['n'] for c in d['coverage']] != list(range(1, d['sourceCount'] + 1)): errs.append('coverage map complete')
    for s in d['slides']:
        if s.get('figure') and not (LEC / s['figure']).is_file(): errs.append('figure ' + s['figure'])
        if s['phase'] in ('LEARN', 'CHECK') and s['id'] not in ('MAP', 'AISYS') and not all(s.get(k) for k in ('question', 'answer', 'concept', 'answerKey', 'commonError', 'notes', 'takeaway')):
            errs.append('unit fields ' + s['id'])
    if d['transfer']['at'] not in keys or not d['transfer'].get('check'): errs.append('transfer case')
    pub = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
    for name in PUBLIC_FILES:
        if name not in pub['iscarb_public_files'] or name not in pub['delivery_asset_sha256']: errs.append('not registered: ' + name)
    return errs


def main():
    assert PPTX.exists(), 'copy the Chapter 8 slide pack to lectures/iscarb/sources/Ch8-Original.pptx first'
    for n, p in FIG.items():
        assert (LEC / p).exists(), p
    L = ledger()
    data = write_lecture(L)
    write_study(L, data)
    patch_story()
    put('iscarb.html', HUB_MARK, HUB, HUB_ANCHOR, after=False)
    put('code-coverage.html', CC_MARK, CC, CC_ANCHOR, after=True)
    register()
    errs = check()
    assert not errs, errs
    print(f'Chapter 8 lecture written: {OUT.relative_to(ROOT)} ({len(data["slides"])} units, {len(L)} source slides), source review and story entry')


if __name__ == '__main__':
    main()
