"""Build midterm-practice.html: a self-graded practice midterm for Chapters 10–14 (English + Arabic).

Questions 1–10 are the Jaheziah practice items from each lecture's Five-objective practice; their English text is read
from the lecture data, so the page stays identical to the lectures. Questions 11–25 and the puzzle (question 26) are
authored here. Every code answer was checked by running the code.
Run:  python3 tools/build_midterm_practice.py
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEC = ROOT / 'lectures/iscarb'
FIG = 'lectures/iscarb/assets/source-vectors/'
FILES = {10: 'Ch10-Dependable-Systems', 11: 'Ch11-Reliability-Engineering', 12: 'Ch12-Safety-Engineering',
         13: 'Ch13-Security-Engineering', 14: 'Ch14-Resilience-Engineering'}


def lecture_quiz(ch: int) -> list:
    s = (LEC / f'{FILES[ch]}.html').read_text(encoding='utf-8')
    return json.loads(re.search(r'<script id="lecture-data" type="application/json">(.*?)</script>', s, re.S).group(1))['quiz']


# ---------- Questions 1–10: Jaheziah practice items from the lectures (Arabic and per-option reasons added here) ----------
JAH = [
 (10, 0, 'أي خاصية من خصائص الاعتمادية يعرّفها Sommerville على أنها حكم (judgment) وليست احتمالاً؟',
  ['التوافرية (Availability)', 'الموثوقية (Reliability)', 'السلامة (Safety)'],
  'التوافرية والموثوقية تُعرَّفان كاحتمالات يمكن قياسها، أما السلامة والأمن والمرونة فأحكام يجب إثباتها بالأدلة.',
  {0: ('Availability is a probability: the service is ready when needed.', 'التوافرية احتمال: أن تكون الخدمة جاهزة عند الحاجة.'),
   1: ('Reliability is a probability: correct service over a stated time.', 'الموثوقية احتمال: خدمة صحيحة خلال فترة محددة.')}),
 (10, 3, 'أي مما يلي دليل على العملية يمكن فحصه؟',
  ['سجل مراجعة له رقم إصدار، فيه الملاحظات وطريقة إغلاقها', 'ملخص ضمان غير موقّع لا يحدد الإصدار', 'لوحة تعرض «نجحت كل الفحوص» بدون السجل الأصلي'],
  'الدليل يجب أن يسمح لشخص آخر بأن يفحص ما الذي رُوجع وكيف حُلّ.',
  {1: ('Without a version or signature, no one can check what it covers.', 'بدون إصدار أو توقيع لا يمكن لأحد أن يتحقق مما يغطيه.'),
   2: ('A summary without the underlying record cannot be inspected.', 'ملخص بدون السجل الأصلي لا يمكن فحصه.')}),
 (11, 1, 'لوحظت ثمانية أعطال محددة في الخدمة خلال 4,000 ساعة. أي زوج وحداته الزمنية صحيحة؟',
  ['ROCOF = 0.002 عطل في الساعة؛ ومقلوبه MTTF = 500 ساعة.', 'POFOD = 0.002 في الساعة؛ وAVAIL = 500 ساعة.', 'ROCOF = 500 عطل في الساعة؛ وMTTF = 0.002 ساعة.', 'AVAIL = 0.002؛ إذن الموثوقية 99.8%.'],
  '8 ÷ 4,000 = 0.002 عطل في الساعة، ومقلوبه 500 ساعة. ولا يمكن حساب التوافرية بدون مدة التوقف ونافذة الخدمة.',
  {1: ('POFOD is per demand, not per hour, and availability is not measured in hours.', 'POFOD يُقاس لكل طلب لا لكل ساعة، والتوافرية لا تُقاس بالساعات.'),
   2: ('The values are inverted: 4,000 ÷ 8 is the time, not the rate.', 'القيم مقلوبة: 4,000 ÷ 8 هو الزمن لا المعدل.'),
   3: ('Availability needs downtime and the service window, which are not given.', 'التوافرية تحتاج مدة التوقف ونافذة الخدمة، وهي غير معطاة.')}),
 (11, 4, 'الاختبارات تستخدم خليط المدخلات من العام الماضي، لكن المستخدمين الآن يعتمدون أساساً على ميزة كانت نادرة. ما الاستنتاج السليم؟',
  ['النسبة المقاسة سابقاً تبقى ضماناً لأي خليط مدخلات.', 'يجب مراجعة الملف التشغيلي (operational profile) والاختبارات الممثِّلة قبل نقل الادعاء.', 'شغّل الحالات النادرة سابقاً فقط وسمِّ النتيجة موثوقية الاستخدام العادي.', 'عُدّ الأخطاء المصلحة في الكود بدل الأعطال.'],
  'الموثوقية أثناء الاستخدام تعتمد على الملف التشغيلي. اختبارات صيد الأخطاء وقياس الموثوقية الممثِّل لهما هدفان مختلفان.',
  {0: ('A measurement holds only for the profile it was measured under.', 'القياس يصح فقط للملف التشغيلي الذي قيس عليه.'),
   2: ('Rare cases alone do not represent normal use.', 'الحالات النادرة وحدها لا تمثل الاستخدام العادي.'),
   3: ('Reliability is measured by failures in use, not faults repaired.', 'الموثوقية تُقاس بالأعطال أثناء الاستخدام، لا بالأخطاء المصلحة.')}),
 (12, 2, 'متى يجوز ضرب احتمالي فرعين تحت بوابة AND؟',
  ['كلما التقى الفرعان عند بوابة AND', 'عندما يُختبر كل فرع على حدة', 'عندما يثبت أن حدثي الفرعين مستقلان'],
  'البوابة تبيّن المنطق فقط. الضرب يفترض الاستقلال، وأي سبب مشترك مثل مصدر كهرباء واحد يكسر هذا الافتراض.',
  {0: ('The gate shows logic, not statistical independence.', 'البوابة تبين المنطق، لا الاستقلال الإحصائي.'),
   1: ('Separate tests do not show that the events cannot fail together.', 'الاختبار المنفصل لا يثبت أن الحدثين لا يفشلان معاً.')}),
 (12, 4, 'تقرير تحليل ساكن (static analysis) بلا أي تحذيرات يدعم أي ادعاء؟',
  ['النظام آمن في بيئة تشغيله', 'أنواع الأخطاء المفحوصة غير موجودة في الكود الذي حُلِّل', 'متطلبات السلامة نفسها صحيحة'],
  'التحليل الساكن يفحص الكود مقابل قواعد محددة. لا يتحقق من صحة المتطلبات ولا من البيئة.',
  {0: ('The analysis never sees the operating environment.', 'التحليل لا يرى بيئة التشغيل أبداً.'),
   2: ('Clean code can still implement wrong requirements.', 'الكود السليم قد ينفذ متطلبات خاطئة.')}),
 (13, 0, 'في نظام مستندات، أي عنصر يمثل ثغرة (vulnerability)؟',
  ['مستند سري لفريق', 'احتمال كشف المستند لفريق آخر', 'غياب فحص الملكية على الخادم'],
  'الأصل (asset) شيء له قيمة، والتهديد (threat) ضرر محتمل، والثغرة ضعف يمكن استغلاله.',
  {0: ('That is the asset: something of value.', 'هذا هو الأصل: شيء له قيمة.'),
   1: ('That is a threat: a possible harm.', 'هذا تهديد: ضرر محتمل.')}),
 (13, 4, 'رُفض طلب من فريق آخر على نقطة وصول (endpoint) واحدة. ماذا تستنتج؟',
  ['هذا الحد صامد في هذا الإصدار؛ والمسارات الأخرى ما زالت تحتاج اختبارات', 'كل نقاط الوصول تطبق نفس القاعدة، إذن النظام آمن', 'تصميم الصلاحيات صحيح لكل الإصدارات القادمة'],
  'الاختبار السلبي الناجح يدعم ادعاءً محدوداً: هذا المستخدم، وهذا العنصر، وهذا المسار، وهذا الإصدار.',
  {1: ('Other endpoints may use a different authorization path.', 'نقاط الوصول الأخرى قد تستخدم مساراً مختلفاً للصلاحيات.'),
   2: ('A future change can break a boundary that holds today.', 'أي تغيير قادم قد يكسر حداً صامداً اليوم.')}),
 (14, 1, 'أي مما يلي اعتمادية تنظيمية (organizational dependency) للاستعادة؟',
  ['الصلاحية والموظفون المدربون اللازمون لتفعيل البديل', 'وحدة التحكم في القرص في الخادم الاحتياطي', 'صيغة الحزم التي تستخدمها الشبكة'],
  'الناس والصلاحيات والتنسيق والتدريب تحدد إن كان البديل التقني سيُستخدم فعلاً.',
  {1: ('A disk controller is a technical dependency.', 'وحدة التحكم في القرص اعتمادية تقنية.'),
   2: ('A packet format is a technical dependency.', 'صيغة الحزم اعتمادية تقنية.')}),
 (14, 2, 'مِمَّ يحذّر نموذج الجبن السويسري (Swiss cheese) لـ Reason؟',
  ['كل طبقة مضافة تمنع كل عطل صُممت له', 'الطبقات التي تبدو مستقلة تفشل دائماً بشكل مستقل', 'نقاط الضعف في عدة طبقات دفاعية قد تصطف معاً'],
  'الحوادث تقع عندما تصطف الثقوب في عدة طبقات دفاعية، والطبقات المتنوعة تقلل احتمال ذلك.',
  {0: ('Every layer has holes; the model says no layer is perfect.', 'كل طبقة فيها ثقوب؛ النموذج يقول إنه لا توجد طبقة كاملة.'),
   1: ('Shared causes can make layers fail together.', 'الأسباب المشتركة قد تجعل الطبقات تفشل معاً.')}),
]

# ---------- Questions 11–25 ----------
Q = [
dict(ch=10, code='''def read_pressure():
    return transmitter_T1.value()

def channel_a():
    return read_pressure() > 8.0

def channel_b():
    p = read_pressure()
    return p > 8.0 and p < 50.0

def must_shut_valve():
    return channel_a() or channel_b()''',
 en='The design document says that channels A and B give two independent ways to shut the valve. What is the BEST assessment?',
 ar='وثيقة التصميم تقول إن القناتين A وB طريقتان مستقلتان لإغلاق الصمام. ما أفضل تقييم؟',
 opts=[('They are not independent: both read transmitter T1, so one T1 fault defeats both channels.', 'ليستا مستقلتين: كلتاهما تقرأ من الحساس T1، فعطل واحد في T1 يُسقط القناتين.'),
       ('They are independent because they are written as separate functions.', 'مستقلتان لأنهما مكتوبتان كدالتين منفصلتين.'),
       ('They are independent because channel B adds an upper-bound check.', 'مستقلتان لأن القناة B تضيف فحصاً للحد الأعلى.'),
       ('Independence does not matter, because the OR needs only one channel.', 'الاستقلال غير مهم، لأن OR تحتاج قناة واحدة فقط.')],
 key=0, why=('Both channels depend on one input. A shared cause defeats redundancy.', 'القناتان تعتمدان على مدخل واحد. السبب المشترك يُسقط التكرار.'),
 wrong={1: ('Separate functions can still share one input.', 'الدوال المنفصلة قد تشترك في مدخل واحد.'),
        2: ('Different logic on the same reading is still one measurement.', 'منطق مختلف على نفس القراءة يبقى قياساً واحداً.'),
        3: ('When T1 fails, both channels fail, so the OR gives no protection.', 'عندما يتعطل T1 تتعطل القناتان، فلا تحمي OR شيئاً.')}),
dict(ch=10, fig=('ch10-source-15.svg', 'Cost rising steeply with the level of dependability, from low to ultra-high'),
 en='The figure relates cost to the level of dependability. A manager asks for “ultra-high” dependability for every module of a university library app, including the book-recommendation page. What is the BEST response?',
 ar='الشكل يربط التكلفة بمستوى الاعتمادية. مدير يطلب اعتمادية «عالية جداً جداً» (ultra-high) لكل أجزاء تطبيق مكتبة الجامعة، بما فيها صفحة اقتراح الكتب. ما أفضل رد؟',
 opts=[('Agree, because higher dependability always pays for itself.', 'أوافق، لأن الاعتمادية الأعلى تعوّض تكلفتها دائماً.'),
       ('Set the target for each service from the consequences of its failure, because cost rises steeply at the top of the scale.', 'أحدد المستوى لكل خدمة حسب عواقب فشلها، لأن التكلفة ترتفع بحدة في أعلى المقياس.'),
       ('Use the lowest level everywhere to save money.', 'أستخدم أقل مستوى في كل مكان لتوفير المال.'),
       ('Read the break-even point from the curve and use that level.', 'أقرأ نقطة التعادل من المنحنى وأستخدم ذلك المستوى.')],
 key=1, why=('Spend on dependability where failure consequences justify it; the cost curve is steep at the top.', 'اصرف على الاعتمادية حيث تبرره عواقب الفشل؛ منحنى التكلفة حاد في أعلاه.'),
 wrong={0: ('The curve shows cost rising steeply, not a return.', 'المنحنى يبين ارتفاع التكلفة بحدة، لا عائداً.'),
        2: ('Some services may still need high dependability.', 'بعض الخدمات قد تحتاج اعتمادية عالية.'),
        3: ('The curve is qualitative; it has no break-even point.', 'المنحنى نوعي؛ ليس فيه نقطة تعادل.')}),
dict(ch=11,
 en='A service has a 99.9% availability requirement over a 720-hour month. Last month it was down for 1.8 hours. What is its availability, and does it meet the requirement?',
 ar='خدمة متطلبها توافرية 99.9% خلال شهر من 720 ساعة. في الشهر الماضي توقفت 1.8 ساعة. كم توافريتها، وهل تحقق المتطلب؟',
 opts=[('99.75%; it does not meet the requirement.', '99.75%؛ لا تحقق المتطلب.'), ('99.75%; it meets the requirement.', '99.75%؛ تحقق المتطلب.'),
       ('99.17%; it does not meet the requirement.', '99.17%؛ لا تحقق المتطلب.'), ('99.98%; it meets the requirement.', '99.98%؛ تحقق المتطلب.')],
 key=0, why=('(720 − 1.8) ÷ 720 = 99.75%. A 99.9% target allows only 0.72 hours of downtime.', '(720 − 1.8) ÷ 720 = 99.75%. هدف 99.9% يسمح بتوقف 0.72 ساعة فقط.'),
 wrong={1: ('99.75% is below 99.9%.', '99.75% أقل من 99.9%.'), 2: ('Uses a wrong downtime value.', 'يستخدم قيمة توقف خاطئة.'), 3: ('Divides by the wrong window.', 'يقسم على نافذة خاطئة.')}),
dict(ch=11, code='''def get_lab_result(patient_id):
    while True:
        reply = lab_server.request(patient_id)
        if reply is not None:
            return reply''',
 en='The lab server sometimes stops responding. Which dependable programming guideline does this code break, and what is the BEST fix?',
 ar='خادم المختبر يتوقف عن الرد أحياناً. أي إرشاد من إرشادات البرمجة الموثوقة يكسره هذا الكود، وما أفضل إصلاح؟',
 opts=[('Check array bounds: add an index check.', 'افحص حدود المصفوفة: أضف فحصاً للفهرس.'),
       ('Name all constants: replace None with a named value.', 'سمِّ كل الثوابت: استبدل None بقيمة لها اسم.'),
       ('Include timeouts when calling external components: stop after a time limit and take a defined failure action.', 'ضع مهلة زمنية عند استدعاء مكونات خارجية: توقف بعد حد زمني ونفّذ إجراء فشل محدداً.'),
       ('Limit the visibility of information: make the function private.', 'قلّل ظهور المعلومات: اجعل الدالة خاصة.')],
 key=2, why=('If the server never replies, the loop waits forever. A timeout returns control so a defined failure action can run.', 'إذا لم يرد الخادم، تنتظر الحلقة للأبد. المهلة الزمنية تعيد التحكم لتنفيذ إجراء فشل محدد.'),
 wrong={0: ('No array is used.', 'لا توجد مصفوفة.'), 1: ('Naming does not stop the endless wait.', 'التسمية لا توقف الانتظار اللانهائي.'), 3: ('Visibility does not stop the endless wait.', 'إخفاء الدالة لا يوقف الانتظار اللانهائي.')}),
dict(ch=12, fig=('ch12-source-21.svg', 'Risk triangle with unacceptable, ALARP and acceptable regions'),
 en='Using the figure: a hazard is not in the unacceptable region, and reducing it further would cost far more than the benefit. Where is it, and what is required?',
 ar='باستخدام الشكل: خطر ليس في المنطقة غير المقبولة، وتقليله أكثر يكلّف أكثر بكثير من فائدته. أين هو، وما المطلوب؟',
 opts=[('Unacceptable region: redesign to remove the hazard.', 'المنطقة غير المقبولة: أعد التصميم لإزالة الخطر.'),
       ('ALARP region: tolerate it, with a recorded justification that further reduction is impractical.', 'منطقة ALARP: يُقبل، مع تبرير مكتوب بأن تقليله أكثر غير عملي.'),
       ('Acceptable region: no action or record is needed.', 'المنطقة المقبولة: لا يلزم أي إجراء أو تسجيل.'),
       ('Negligible risk: remove it from the hazard log.', 'خطر مهمل: احذفه من سجل الأخطار.')],
 key=1, why=('In the ALARP region, risk is tolerated only when further reduction is impractical or excessively expensive, and that must be justified.', 'في منطقة ALARP يُقبل الخطر فقط عندما يكون تقليله أكثر غير عملي أو مكلفاً جداً، ويجب تبرير ذلك.'),
 wrong={0: ('The question rules out the unacceptable region.', 'السؤال يستبعد المنطقة غير المقبولة.'),
        2: ('The acceptable region is for low risks; this one is not low.', 'المنطقة المقبولة للمخاطر المنخفضة؛ وهذا ليس منخفضاً.'),
        3: ('Hazards are not removed from the log by assumption.', 'الأخطار لا تُحذف من السجل بالافتراض.')}),
dict(ch=12, code='''MAX_SINGLE = 4    # units
MAX_DAILY = 25    # units

def allow_dose(dose, given_today):
    if dose <= 0:
        return False
    return dose <= MAX_SINGLE''',
 en='The pump’s safety requirements are: a single dose ≤ 4 units, and the total in one day ≤ 25 units. A tester requests 4 units seven times in one day. Which is TRUE?',
 ar='متطلبا السلامة للمضخة: الجرعة الواحدة ≤ 4 وحدات، ومجموع اليوم ≤ 25 وحدة. المختبِر يطلب 4 وحدات سبع مرات في يوم واحد. أي عبارة صحيحة؟',
 opts=[('The seventh dose is refused, because the total would exceed 25.', 'الجرعة السابعة تُرفض، لأن المجموع سيتجاوز 25.'),
       ('All seven doses are allowed (28 units): the daily limit is never checked.', 'الجرعات السبع كلها تُسمح (28 وحدة): الحد اليومي لا يُفحص أبداً.'),
       ('The first dose is refused, because 4 is not below the maximum.', 'الجرعة الأولى تُرفض، لأن 4 ليست أقل من الحد.'),
       ('The function raises an error on the seventh call.', 'الدالة تُظهر خطأً في الاستدعاء السابع.')],
 key=1, why=('given_today is never used, so the daily requirement is not implemented. A per-dose limit says nothing about the total.', 'المتغير given_today لا يُستخدم، فمتطلب الحد اليومي غير منفذ. حد الجرعة الواحدة لا يقول شيئاً عن المجموع.'),
 wrong={0: ('given_today is never compared with MAX_DAILY.', 'given_today لا يُقارن أبداً بـ MAX_DAILY.'), 2: ('The check is ≤, so 4 is allowed.', 'الفحص ≤، إذن 4 مسموحة.'), 3: ('Nothing in the code raises an error.', 'لا شيء في الكود يُظهر خطأً.')}),
dict(ch=13, fig=('ch13-source-40.svg', 'Misuse case diagram: a medical receptionist’s use cases and an attacker’s misuse cases, Impersonate receptionist and Intercept transfer'),
 en='In the misuse-case diagram, the attacker’s “Intercept transfer” threatens which use case, and which type of threat is it?',
 ar='في مخطط حالات سوء الاستخدام، «Intercept transfer» الخاصة بالمهاجم تهدد أي حالة استخدام، وما نوع التهديد؟',
 opts=[('View patient info; modification', 'عرض بيانات المريض؛ تعديل (modification)'), ('Transfer data; interception', 'نقل البيانات؛ اعتراض (interception)'),
       ('Contact patient; fabrication', 'التواصل مع المريض؛ تزييف (fabrication)'), ('Register patient; interruption', 'تسجيل المريض؛ تعطيل (interruption)')],
 key=1, why=('Intercepting data while it is transferred is interception: an attacker gains access to an asset.', 'اعتراض البيانات أثناء نقلها هو interception: المهاجم يصل إلى أصل.'),
 wrong={0: ('Intercepting reads data in transit; it does not change it.', 'الاعتراض يقرأ البيانات أثناء النقل ولا يغيرها.'), 2: ('Fabrication creates false information.', 'التزييف يُنشئ معلومات كاذبة.'), 3: ('Interruption makes a service unavailable.', 'التعطيل يجعل الخدمة غير متاحة.')}),
dict(ch=13, code='''def can_download(user, doc):
    if user.get("logged_in"):
        if doc["team"] in user.get("teams", []):
            return True
        return user.get("role") == "admin"
    return True   # the server log will catch misuse

DOC = {"team": "A"}''',
 en='What does <code>can_download({}, DOC)</code> return, and which secure-design guideline does the last line break?',
 ar='ماذا تُرجع <code>can_download({}, DOC)</code>، وأي إرشاد من إرشادات التصميم الآمن يكسره السطر الأخير؟',
 opts=[('False; no guideline is broken.', 'False؛ لا يُكسر أي إرشاد.'), ('True; log user actions.', 'True؛ سجّل أفعال المستخدم.'),
       ('It raises a KeyError; check all inputs.', 'تُظهر KeyError؛ افحص كل المدخلات.'), ('True; fail securely.', 'True؛ افشل بأمان (fail securely).')],
 key=3, why=('An empty user is not logged in, so the function reaches the last line and grants access. When access cannot be established, the system must deny it.', 'المستخدم الفارغ غير مسجل دخول، فتصل الدالة للسطر الأخير وتسمح بالوصول. عندما لا يمكن إثبات الصلاحية يجب أن يرفض النظام.'),
 wrong={0: ('The last line returns True.', 'السطر الأخير يُرجع True.'), 1: ('A log records misuse after the fact; it does not prevent it.', 'السجل يوثق سوء الاستخدام بعد وقوعه ولا يمنعه.'), 2: ('.get() returns None instead of raising an error.', 'الدالة ‎.get()‎ تُرجع None ولا تُظهر خطأً.')}),
dict(ch=14, fig=('ch14-source-8.svg', 'State diagram of recognition, resistance, recovery and reinstatement'),
 en='In the state diagram, the system is in Resistance. The attack succeeds. Which state comes next, and what is its goal?',
 ar='في مخطط الحالات، النظام في مرحلة المقاومة (Resistance). الهجوم ينجح. ما الحالة التالية، وما هدفها؟',
 opts=[('Recognition: detect the attack.', 'التعرف (Recognition): اكتشاف الهجوم.'), ('Reinstatement: restore all services.', 'الإعادة الكاملة (Reinstatement): إرجاع كل الخدمات.'),
       ('Recovery: keep critical services running and repair the system.', 'الاستعادة (Recovery): إبقاء الخدمات الحرجة وإصلاح النظام.'), ('Normal operation: the attack is repelled.', 'التشغيل العادي: صُدّ الهجوم.')],
 key=2, why=('A successful attack moves the system to recovery: critical services first, then repair.', 'الهجوم الناجح ينقل النظام إلى الاستعادة: الخدمات الحرجة أولاً ثم الإصلاح.'),
 wrong={0: ('Recognition came before resistance.', 'التعرف جاء قبل المقاومة.'), 1: ('Reinstatement follows a completed repair.', 'الإعادة الكاملة تأتي بعد اكتمال الإصلاح.'), 3: ('That path is taken only when the attack is repelled.', 'هذا المسار فقط عند صدّ الهجوم.')}),
dict(ch=14, fig=('ch14-source-46.svg', 'Survivable systems analysis: four stages in a cycle'),
 en='Your team has finished stage 2 in the figure for a hospital pharmacy system. What should you do NEXT?',
 ar='فريقك أنهى المرحلة 2 في الشكل لنظام صيدلية مستشفى. ماذا تفعل بعدها؟',
 opts=[('Identify softspots and choose survivability strategies.', 'حدد نقاط الضعف (softspots) واختر استراتيجيات البقاء.'), ('Identify attacks and the components each attack could compromise.', 'حدد الهجمات والمكونات التي يمكن لكل هجوم أن يخترقها.'),
       ('Review the system requirements and architecture again.', 'راجع متطلبات النظام وبنيته مرة أخرى.'), ('Buy an intrusion detection system.', 'اشترِ نظاماً لكشف التسلل.')],
 key=1, why=('Stage 3 comes after critical services are identified: describe attacks and the components they could compromise.', 'المرحلة 3 تأتي بعد تحديد الخدمات الحرجة: وصف الهجمات والمكونات التي يمكن اختراقها.'),
 wrong={0: ('That is stage 4.', 'هذه المرحلة 4.'), 2: ('That is stage 1, already done.', 'هذه المرحلة 1، وقد انتهت.'), 3: ('Buying a tool is not a stage of the method.', 'شراء أداة ليس مرحلة من مراحل الطريقة.')}),
dict(ch=10,
 en='Your team used model checking to show that the pump switch-over model never reaches a state where both pumps are off. The regulator asks: “So the pumps in the plant can never both stop?” What is the BEST answer?',
 ar='فريقك استخدم فحص النماذج (model checking) ليبين أن نموذج تبديل المضخات لا يصل أبداً لحالة تكون فيها المضختان متوقفتين. الجهة الرقابية تسأل: «إذن المضختان في المحطة لا يمكن أن تتوقفا معاً أبداً؟» ما أفضل إجابة؟',
 opts=[('Yes. The model checker examined every reachable state.', 'نعم. فاحص النماذج فحص كل حالة يمكن الوصول إليها.'), ('No. Model checking says nothing useful about the plant.', 'لا. فحص النماذج لا يقول شيئاً مفيداً عن المحطة.'),
       ('The model satisfies the property; we still need evidence that the model matches the plant, that the sensors work and that the requirements are complete.', 'النموذج يحقق الخاصية؛ وما زلنا نحتاج دليلاً على أن النموذج يطابق المحطة، وأن الحساسات تعمل، وأن المتطلبات مكتملة.'),
       ('Yes, once static analysis has also been run on the code.', 'نعم، بعد تشغيل التحليل الساكن على الكود أيضاً.')],
 key=2, why=('A model check covers the model under its assumptions. The plant, the sensors and the completeness of the requirements need their own evidence.', 'فحص النموذج يغطي النموذج ضمن افتراضاته. المحطة والحساسات واكتمال المتطلبات تحتاج أدلتها الخاصة.'),
 wrong={0: ('The result covers the model, not the physical plant.', 'النتيجة تغطي النموذج، لا المحطة الفعلية.'), 1: ('It is real evidence about the logic, within its assumptions.', 'هو دليل حقيقي على المنطق، ضمن افتراضاته.'), 3: ('Static analysis does not validate the model or the environment.', 'التحليل الساكن لا يتحقق من النموذج ولا من البيئة.')}),
dict(ch=11, fig=('ch11-source-47.svg', 'N-version programming: three versions feed an output selector'), code='''def output_selector(v1, v2, v3):
    if v1 == v2 or v1 == v3:
        return v1
    if v2 == v3:
        return v2
    raise RuntimeError("no majority")''',
 en='Three teams built versions 1–3 from the same specification. The output selector is shown above. The versions return 18, 24 and 18. Which is TRUE?',
 ar='ثلاثة فرق بنت النسخ 1 إلى 3 من نفس المواصفات. دالة اختيار المخرجات معروضة أعلاه. النسخ تُرجع 18 و24 و18. أي عبارة صحيحة؟',
 opts=[('It returns 24, the value that differs.', 'تُرجع 24، القيمة المختلفة.'), ('It returns 18, which is guaranteed to be correct because two versions agree.', 'تُرجع 18، وهي صحيحة بالتأكيد لأن نسختين اتفقتا.'),
       ('It returns 18; but if the shared specification is wrong, two versions can agree on a wrong value.', 'تُرجع 18؛ لكن إذا كانت المواصفات المشتركة خاطئة، قد تتفق نسختان على قيمة خاطئة.'), ('It raises RuntimeError, because the three values differ.', 'تُظهر RuntimeError لأن القيم الثلاث مختلفة.')],
 key=2, why=('v1 equals v3, so the selector returns 18. Voting masks one different version; it does not detect an error in the common specification.', 'v1 تساوي v3، فتُرجع الدالة 18. التصويت يُخفي نسخة واحدة مختلفة، لكنه لا يكشف خطأً في المواصفات المشتركة.'),
 wrong={0: ('The selector returns the majority, not the odd value.', 'الدالة تُرجع الأغلبية، لا القيمة المختلفة.'), 1: ('Agreement is not correctness; a common specification error defeats the vote.', 'الاتفاق ليس صحة؛ خطأ المواصفات المشترك يُسقط التصويت.'), 3: ('Two of the three values agree.', 'قيمتان من الثلاث متفقتان.')}),
dict(ch=12, code='''def compute_dose(r0, r1, r2, max_dose):
    if r2 > r1 and (r2 - r1) >= (r1 - r0):
        dose = round((r2 - r1) / 4)
    elif r2 <= r1:
        dose = 0
    else:
        dose = 1
    if dose > max_dose:
        dose = max_dose
    if dose == 0 and r2 > 12:      # added later
        dose = 2
    return dose''',
 en='The safety argument must show that <code>compute_dose</code> never returns more than <code>max_dose</code>. A developer later added the last <code>if</code>. Which input shows that the property is violated?',
 ar='حجة السلامة يجب أن تثبت أن <code>compute_dose</code> لا تُرجع أبداً أكثر من <code>max_dose</code>. أضاف مطور لاحقاً جملة <code>if</code> الأخيرة. أي مدخل يثبت أن الخاصية مكسورة؟',
 opts=[('r0=5, r1=8, r2=12, max_dose=4', 'r0=5, r1=8, r2=12, max_dose=4'), ('r0=14, r1=14, r2=13, max_dose=1', 'r0=14, r1=14, r2=13, max_dose=1'),
       ('r0=5, r1=8, r2=20, max_dose=4', 'r0=5, r1=8, r2=20, max_dose=4'), ('r0=10, r1=10, r2=10, max_dose=1', 'r0=10, r1=10, r2=10, max_dose=1')],
 key=1, why=('r2 ≤ r1 gives dose 0; then r2 > 12 sets dose to 2, after the cap was applied, so 2 > max_dose = 1. A safety argument must check every path to the exit.', 'r2 ≤ r1 تعطي جرعة 0؛ ثم r2 > 12 تجعلها 2 بعد تطبيق الحد، فتصبح 2 > max_dose = 1. حجة السلامة يجب أن تفحص كل مسار يصل إلى المخرج.'),
 wrong={0: ('Returns 1, within the limit.', 'تُرجع 1، ضمن الحد.'), 2: ('Returns 3, within the limit.', 'تُرجع 3، ضمن الحد.'), 3: ('Returns 0: r2 is not above 12.', 'تُرجع 0: لأن r2 ليست أكبر من 12.')}),
dict(ch=13, fig=('ch13-source-56.svg', 'Layered protection: platform level, application level and record level'),
 en='A records system uses the three protection levels shown. All three check the same directory account and password. What is the MOST significant weakness?',
 ar='نظام سجلات يستخدم مستويات الحماية الثلاثة الظاهرة. المستويات الثلاثة كلها تتحقق من نفس الحساب وكلمة المرور في الدليل. ما أهم نقطة ضعف؟',
 opts=[('Three levels make the system too slow to use.', 'المستويات الثلاثة تجعل النظام بطيئاً جداً.'), ('One stolen credential opens all three levels, so they are not independent defenses.', 'سرقة بيانات دخول واحدة تفتح المستويات الثلاثة، فهي ليست دفاعات مستقلة.'),
       ('Record-level checks should run before platform checks.', 'فحوص مستوى السجل يجب أن تسبق فحوص المنصة.'), ('The platform level should be removed to reduce cost.', 'يجب حذف مستوى المنصة لتقليل التكلفة.')],
 key=1, why=('Layers protect only when each fails in a different way. A shared credential is a common cause for all three.', 'الطبقات تحمي فقط عندما تفشل كل واحدة بطريقة مختلفة. بيانات الدخول المشتركة سبب مشترك للثلاثة.'),
 wrong={0: ('Overhead matters, but it is not the main weakness.', 'العبء مهم، لكنه ليس الضعف الرئيسي.'), 2: ('Changing the order does not fix a shared credential.', 'تغيير الترتيب لا يعالج بيانات الدخول المشتركة.'), 3: ('Removing a level does not address the shared weakness.', 'حذف مستوى لا يعالج الضعف المشترك.')}),
dict(ch=14, code='''def merge(central, offline):
    return central + offline

central = [{"id": "r1"}, {"id": "r2"}]
offline = [{"id": "r2"}, {"id": "r3"}]
print(len(merge(central, offline)))''',
 en='During an outage, staff recorded admissions offline. Record r2 was entered in both systems. When the central system returns, this code merges the records. What does it print, and what is the problem?',
 ar='أثناء انقطاع، سجّل الموظفون حالات الدخول بدون اتصال. السجل r2 أُدخل في النظامين. عندما يعود النظام المركزي، يدمج هذا الكود السجلات. ماذا يطبع، وما المشكلة؟',
 opts=[('3; the merge is correct.', '3؛ الدمج صحيح.'), ('4; r2 is now duplicated, so reconciliation must match records by their identity.', '4؛ السجل r2 صار مكرراً، فالمطابقة يجب أن تتم حسب هوية السجل.'),
       ('4; this is correct, because offline records are always new.', '4؛ وهذا صحيح لأن السجلات غير المتصلة جديدة دائماً.'), ('It raises an error, because the lists overlap.', 'يُظهر خطأً لأن القائمتين متداخلتان.')],
 key=1, why=('List addition keeps every element, so r2 appears twice. After degraded operation, fallback records must be reconciled with the authoritative system by identity.', 'جمع القوائم يحتفظ بكل العناصر، فيظهر r2 مرتين. بعد التشغيل المتدهور يجب مطابقة السجلات البديلة مع النظام الأساسي حسب الهوية.'),
 wrong={0: ('List addition keeps every element: 2 + 2 = 4.', 'جمع القوائم يحتفظ بكل العناصر: 2 + 2 = 4.'), 2: ('r2 already existed in the central system.', 'السجل r2 كان موجوداً في النظام المركزي.'), 3: ('Adding two lists never raises an error.', 'جمع قائمتين لا يُظهر خطأً أبداً.')}),
]

# ---------- Question 26: the puzzle ----------
PIECES = [  # id, en, ar, correct slot (or None)
 ('P1', 'Restore last night’s backup and reconnect every console at once.', 'استرجع نسخة الليلة الماضية الاحتياطية وأعد توصيل كل الأجهزة دفعة واحدة.', None,
  ('Skips the integrity check of the backup and loses calls taken since. It also leaves no service during the hours restoration takes.', 'يتجاوز فحص سلامة النسخة الاحتياطية ويضيّع المكالمات المسجلة بعدها، ولا يقدم خدمة خلال ساعات الاستعادة.')),
 ('P2', 'Call-taking shall be available at least 99.99% of each 720-hour month (at most 4.3 minutes down), measured from the switch log.', 'خدمة استقبال المكالمات يجب أن تكون متاحة 99.99% على الأقل من كل شهر مدته 720 ساعة (توقف 4.3 دقائق كحد أقصى)، وتُقاس من سجل المقسم.', '1', None),
 ('P3', 'A second identical server in the same rack, switched over by the on-call engineer (about 30 minutes).', 'خادم ثانٍ مطابق في نفس الحامل، يحوّل إليه المهندس المناوب (حوالي 30 دقيقة).', None,
  ('Keeps the shared rack and power (a common cause), and a 30-minute manual switch-over breaks the 4.3-minute limit.', 'يُبقي الحامل والكهرباء المشتركين (سبب مشترك)، والتحويل اليدوي في 30 دقيقة يكسر حد 4.3 دقائق.')),
 ('P4', 'The tablet menu hides patients from other incidents.', 'قائمة الجهاز اللوحي تُخفي مرضى الحوادث الأخرى.', None,
  ('Hiding links in the interface is not access control; the server still returns any record.', 'إخفاء الروابط في الواجهة ليس تحكماً في الوصول؛ الخادم ما زال يُرجع أي سجل.')),
 ('P5', 'Before dispatch, the system checks the address against the caller’s location and district; on a mismatch it blocks dispatch until the dispatcher confirms.', 'قبل الإرسال، يقارن النظام العنوان بموقع المتصل وحيّه؛ وعند عدم التطابق يوقف الإرسال حتى يؤكد الموظف.', '3', None),
 ('P6', 'The dispatch system shall have no more than 2 failures per month.', 'نظام الإرسال يجب ألا يتعطل أكثر من مرتين في الشهر.', None,
  ('Counts failures but says nothing about how long each lasts, so it cannot enforce the 4.3-minute limit.', 'يعدّ الأعطال لكنه لا يقول شيئاً عن مدة كل عطل، فلا يضمن حد 4.3 دقائق.')),
 ('P7', 'The server returns a patient record only to a paramedic assigned to that patient’s current incident.', 'الخادم يُرجع سجل المريض فقط للمسعف المكلف بحادثة ذلك المريض الحالية.', '4', None),
 ('P8', 'Every dispatch is logged for a weekly review.', 'كل عملية إرسال تُسجل لمراجعتها أسبوعياً.', None,
  ('A log records the wrong dispatch after the ambulance has gone; it does not prevent it.', 'السجل يوثق الإرسال الخاطئ بعد ذهاب الإسعاف؛ ولا يمنعه.')),
 ('P9', 'Automatic failover to a second server in another building, with its own power supply and a separately tested software release.', 'تحويل تلقائي إلى خادم ثانٍ في مبنى آخر، بمصدر كهرباء مستقل وإصدار برمجي مختبر بشكل منفصل.', '2', None),
 ('P10', 'Numbered paper dispatch cards, activated by the named shift lead and entered by incident ID once the system is restored.', 'بطاقات إرسال ورقية مرقمة، يفعّلها مشرف المناوبة المسمّى، وتُدخل حسب رقم الحادثة بعد استعادة النظام.', '5', None),
]
SLOTS = [
 ('1', 'Reliability requirement for call-taking', 'متطلب الاعتمادية لاستقبال المكالمات', 11, 'F1 limits downtime, so the requirement must be availability with a value and a time window.', 'الحقيقة F1 تحدد مدة التوقف، فالمتطلب يجب أن يكون توافرية بقيمة ونافذة زمنية.'),
 ('2', 'Architecture of the dispatch servers', 'بنية خوادم الإرسال', 10, 'F2 is a common cause. Diversity of site, power and release removes it, and automatic failover fits the 4.3-minute limit.', 'الحقيقة F2 سبب مشترك. تنويع الموقع والكهرباء والإصدار يزيله، والتحويل التلقائي يناسب حد 4.3 دقائق.'),
 ('3', 'Control for the wrong-address hazard', 'التحكم في خطر العنوان الخاطئ', 12, 'F3 is a hazard. Checking the address before dispatch detects and removes it before an accident.', 'الحقيقة F3 خطر. فحص العنوان قبل الإرسال يكتشفه ويزيله قبل وقوع الحادث.'),
 ('4', 'Access control on paramedic tablets', 'التحكم في الوصول على أجهزة المسعفين', 13, 'F4 needs authorization enforced on the server, for each actor and record.', 'الحقيقة F4 تحتاج صلاحيات يفرضها الخادم لكل مستخدم وسجل.'),
 ('5', 'Continuity plan for a ransomware attack', 'خطة الاستمرارية عند هجوم فدية', 14, 'F5 means restoration can take hours, longer than slot 1 allows, so a degraded mode with a named owner and reconciliation is needed.', 'الحقيقة F5 تعني أن الاستعادة قد تأخذ ساعات، أطول مما تسمح به الخانة 1، فيلزم وضع تشغيل متدهور له مسؤول مسمّى ومطابقة للسجلات.'),
]
FACTS = [
 ('F1', 'The contract allows call-taking to be down for at most 4.3 minutes in any 720-hour month.', 'العقد يسمح بتوقف استقبال المكالمات 4.3 دقائق كحد أقصى في أي شهر مدته 720 ساعة.'),
 ('F2', 'Today the two dispatch servers share one power feed, one rack and the same software release.', 'حالياً خادما الإرسال يشتركان في مصدر كهرباء واحد، وحامل واحد، ونفس الإصدار البرمجي.'),
 ('F3', 'Last year an ambulance went to a street with the same name in another district.', 'في العام الماضي ذهبت سيارة إسعاف إلى شارع بنفس الاسم في حي آخر.'),
 ('F4', 'Paramedic tablets can currently open every patient record in the region.', 'أجهزة المسعفين اللوحية تستطيع حالياً فتح كل سجلات المرضى في المنطقة.'),
 ('F5', 'A nearby region lost its dispatch system to ransomware last year; restoring it took 6 hours.', 'منطقة مجاورة فقدت نظام الإرسال بسبب هجوم فدية العام الماضي، واستغرقت استعادته 6 ساعات.'),
]


def build_data() -> dict:
    items = []
    for ch, n, ar, ar_opts, ar_why, wrong in JAH:
        q = lecture_quiz(ch)[n]
        assert len(ar_opts) == len(q['options']), (ch, n)
        items.append(dict(ch=ch, en=html.escape(q['q']), ar=ar,
                          opts=[[html.escape(e), a] for e, a in zip(q['options'], ar_opts)], key=q['answer'],
                          why=[html.escape(q['why']), ar_why], wrong={str(k): list(v) for k, v in wrong.items()}))
    for q in Q:
        it = dict(ch=q['ch'], en=q['en'], ar=q['ar'], opts=[list(o) for o in q['opts']], key=q['key'], why=list(q['why']),
                  wrong={str(k): list(v) for k, v in q['wrong'].items()})
        if q.get('fig'):
            path = FIG + q['fig'][0]
            assert (ROOT / path).is_file(), path
            it['fig'] = [path, q['fig'][1]]
        if q.get('code'):
            it['code'] = html.escape(q['code'])
        items.append(it)
    for it in items:  # every wrong option has a reason
        assert set(it['wrong']) == {str(i) for i in range(len(it['opts'])) if i != it['key']}, it['en'][:60]
    assert len(items) == 25
    pieces = [dict(id=p, en=e, ar=a, slot=s, no=list(n) if n else None) for p, e, a, s, n in PIECES]
    slots = [dict(id=i, en=e, ar=a, ch=c, why=[we, wa]) for i, e, a, c, we, wa in SLOTS]
    assert sorted(p['slot'] for p in pieces if p['slot']) == ['1', '2', '3', '4', '5']
    return dict(items=items, puzzle=dict(facts=[list(f) for f in FACTS], slots=slots, pieces=pieces))


PUZZLE_SVG = '''<svg viewBox="0 0 760 330" role="img" aria-label="Five slots around a dependable dispatch system" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, Segoe UI, sans-serif"><rect width="760" height="330" fill="#ffffff"/><g stroke="#8a9a94" stroke-width="2" stroke-dasharray="6 5"><line x1="120" y1="58" x2="380" y2="165"/><line x1="640" y1="58" x2="380" y2="165"/><line x1="120" y1="273" x2="380" y2="165"/><line x1="640" y1="273" x2="380" y2="165"/><line x1="380" y1="288" x2="380" y2="205"/></g><rect x="270" y="125" width="220" height="80" rx="10" fill="#e1efeb" stroke="#0f6b62" stroke-width="2"/><text x="380" y="160" text-anchor="middle" font-size="17" font-weight="700" fill="#0f2f2b">Dependable</text><text x="380" y="183" text-anchor="middle" font-size="17" font-weight="700" fill="#0f2f2b">dispatch system</text>SLOTS</svg>'''


def puzzle_svg() -> str:
    pos = [(20, 20), (540, 20), (20, 235), (540, 235), (280, 250)]
    out = []
    for (x, y), (n, en, _, ch, *_r) in zip(pos, SLOTS):
        out.append(f'<path d="M{x} {y} h85 a12 12 0 0 1 24 0 h91 v76 h-200 z" fill="#ffffff" stroke="#18201d" stroke-width="2"/>'
                   f'<text x="{x+100}" y="{y+28}" text-anchor="middle" font-size="15" font-weight="700" fill="#18201d">Slot {n}</text>'
                   f'<text x="{x+100}" y="{y+49}" text-anchor="middle" font-size="12.5" fill="#18201d">{html.escape(en.split(" for ")[0].split(" on ")[0])}</text>'
                   f'<text x="{x+100}" y="{y+67}" text-anchor="middle" font-size="12" fill="#5b6762">Ch{ch}</text>')
    return PUZZLE_SVG.replace('SLOTS', ''.join(out))


def main() -> int:
    page = ROOT / 'midterm-practice.html'
    tpl = (ROOT / 'tools/midterm-practice.template.html').read_text(encoding='utf-8')
    data = json.dumps(build_data(), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    out = tpl.replace('/*DATA*/null', data).replace('<!--PUZZLE-SVG-->', puzzle_svg())
    assert '/*DATA*/' not in out and '<!--PUZZLE-SVG-->' not in out
    page.write_text(out, encoding='utf-8')
    print(f'Wrote {page.name}: 25 questions + puzzle, {len(out):,} bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
