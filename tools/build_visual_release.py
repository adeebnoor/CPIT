"""Refresh the reviewed visual lecture release and its reusable teaching guide."""
from pathlib import Path
import argparse,json,subprocess
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]

def insert(path,ident,markup,after_heading=False):
    p=ROOT/path;s=BeautifulSoup(p.read_text(),'html.parser')
    existing=s.find(id=ident)
    if existing:existing.decompose()
    part=BeautifulSoup(markup,'html.parser').find('section');part['id']=ident
    heading=s.select_one('.document-heading')
    if after_heading and heading:heading.insert_after(part)
    else:s.find('main').append(part)
    p.write_text(str(s))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path);args=parser.parse_args()
    if args.input:subprocess.run(['python',str(ROOT/'tools/build_learning_path.py'),'--input',str(args.input)],check=True)
    p=ROOT/'curriculum/publication.json';cat=json.loads(p.read_text());cat['release']='20260921-visual-v3';cat['status']='Nine visual learning paths with paginated explanations, complete source ledgers, required preparation and preserved assignments.'
    cat['lectures']=json.loads((ROOT/'curriculum/learning-path/lectures.json').read_text());p.write_text(json.dumps(cat,indent=2))
    insert('iscarb.html','visual-release','''<section class="section"><p class="ey">A CLEARER CLASSROOM ROUTE</p><h2>One concept. One visual. A decision you can explain.</h2><p>Use Back and Next to move through the lecture. Open <b>Details</b> for the complete explanation; longer material continues on numbered pages. Required reading and assignments stay clearly labelled.</p><p><a class="text-link" href="instructor-guide.html#use-iscarb">Teach with iSCARB: method and reusable planning sheet →</a></p></section>''')
    insert('student-guide.html','visual-navigation','''<section class="panel"><h2>Navigate the visual lectures</h2><ol><li><b>Start with the case.</b> Identify the decision and what remains unknown.</li><li><b>Follow the visual overview.</b> Each concept has a diagram or source figure and a short takeaway.</li><li><b>Open Details when you need the explanation.</b> Back and Next move through numbered pages before the next concept. Use Units to jump.</li><li><b>Attempt the checks before revealing answers.</b> Complete the named reading and apply its concept in the assignment.</li></ol><p>Arrow keys and Page Up / Page Down also navigate. Tab moves between controls. Local saving remains separate from Blackboard submission.</p></section>''',True)
    insert('instructor-guide.html','use-iscarb','''<section class="panel"><p class="ey">USE ISCARB IN YOUR TEACHING</p><h2>A repeatable teaching sequence</h2><ol><li><b>SEE:</b> begin with a specific situation and a decision that requires explanation.</li><li><b>EXPLAIN:</b> connect each concept to one purposeful visual and one short takeaway. Keep the full source and qualifications in Details.</li><li><b>TEST:</b> use two brief retrieval checks. Reveal explanations after students reason individually or with a partner.</li><li><b>DECIDE:</b> use one application stop to build an artifact, inspect evidence and state a boundary. Transfer the reasoning to a new assignment case.</li></ol><p><a class="text-link" href="iSCARB-Teaching-Template.md" download>Download the editable iSCARB teaching planning sheet</a></p><p>Developed by Professor Adeeb Noor. Adapt the subject, objectives and case to your course. Use the actual quality of reasoning and later transfer to evaluate learning; slide completion is not mastery.</p><p>Design comparison: <a href="https://web.mit.edu/6.102/www/sp25/general/">MIT 6.102</a> integrates preparation, exercises and feedback. <a href="https://www.w3.org/WAI/WCAG22/Understanding/reflow.html">W3C reflow guidance</a> requires preserving access to information and functionality when content is enlarged. Here, long lecture content is paginated instead of compressed into smaller text. This is an implementation direction, not a claim of institutional equivalence or verified WCAG conformance.</p></section>''',True)
    print('Visual release catalog, student navigation guide and reusable teaching guide refreshed.')

if __name__=='__main__':main()
