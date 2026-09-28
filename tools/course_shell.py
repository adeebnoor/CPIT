"""Shared presentation chrome; assessment content remains independently pinned."""
from pathlib import Path
import re

VERSION = '20260928-campus-v3'
ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'https://adeebnoor.github.io/'

def header(prefix='', current='', surface='document'):
    links = [('iscarb.html','Learning path'),('student-guide.html','How to study'),
             ('course-resources.html','Course & sources'),('nelc-alignment.html','Saudi alignment'),
             ('methodology.html','For educators')]
    nav=''.join(f'<a href="{prefix}{url}"'+(' aria-current="page"' if current==url else '')+f'>{label}</a>' for url,label in links)
    return f'''<header class="site-header" data-surface="{surface}"><div class="site-masthead">
<a class="site-brand" href="{prefix}iscarb.html"><img src="{prefix}assets/fcit-kau-logo.png" width="48" height="48" alt="FCIT, King Abdulaziz University"><span><strong>iSCARB</strong><small>CPIT-455 · King Abdulaziz University</small></span></a>
<div class="site-utilities"><a class="profile-link" href="{PROFILE}">About &amp; contact <span aria-hidden="true">↗</span></a><button class="theme" id="themeBtn" type="button">Dark mode</button></div>
<button class="nav-toggle" id="navToggle" type="button" aria-controls="courseNav" aria-expanded="false">Menu <span aria-hidden="true">☰</span></button></div>
<nav class="site-nav" id="courseNav" aria-label="Course navigation">{nav}<a href="https://qeeem.com/" id="topQeeem" target="_blank" rel="noopener">Evaluation <span aria-hidden="true">↗</span></a></nav></header>'''

def footer(prefix=''):
    return f'''<footer class="site-footer"><div class="site-footer-inner"><div><a class="footer-brand" href="{prefix}iscarb.html">iSCARB</a><p>Software Engineering II · CPIT-455<br>Faculty of Computing &amp; Information Technology<br>King Abdulaziz University · Jeddah, Saudi Arabia</p></div><div><h2>Explore the course</h2><a href="{prefix}student-guide.html">Student guide</a><a href="{prefix}course-resources.html">Course &amp; sources</a><a href="{prefix}nelc-alignment.html">Saudi alignment</a></div><div><h2>Teaching &amp; collaboration</h2><a href="{prefix}methodology.html">iSCARB methodology</a><a href="{prefix}instructor-guide.html">Instructor guide</a><a href="{prefix}index.html#evolution">Teaching history</a></div><div><h2>Professor Adeeb Noor</h2><p>Course instructor &amp; iSCARB developer</p><a class="profile-link" href="{PROFILE}">Profile, research &amp; contact ↗</a><a href="mailto:arnoor@kau.edu.sa">arnoor@kau.edu.sa</a></div></div><div class="site-footer-bottom"><span>Learning resources · Human judgment · Evidence</span><a href="#top">Back to top ↑</a></div></footer>'''

def dependencies(prefix=''):
    return f'''<link rel="stylesheet" href="{prefix}course-shell.css?v={VERSION}"><script src="{prefix}course-shell.js?v={VERSION}" defer></script><script>try{{document.documentElement.dataset.theme=localStorage.getItem('iscarb-theme')==='dark'?'dark':'light'}}catch(e){{document.documentElement.dataset.theme='light'}}</script>'''

def assessment_blocks():
    return {
        'head': dependencies('../../'),
        'header': '<span id="top"></span>'+header('../../', surface='assignment'),
        'footer': footer('../../'),
    }

def block(name, content):
    return f'<!-- course-presentation:{name}:start -->{content}<!-- course-presentation:{name}:end -->'

def strip_assessment_presentation(text):
    """Remove only the exact shared chrome; reject altered or extra decorators.

    The original assignment SHA remains the authority for every other byte,
    including all task text, local draft IDs, inline scripts and STRESS logic.
    """
    for name, content in assessment_blocks().items():
        expected=block(name, content)
        if f'course-presentation:{name}:start' in text:
            if text.count(expected)!=1:
                raise ValueError(f'Unexpected assessment presentation block: {name}')
            text=text.replace(expected,'',1)
    if 'course-presentation:' in text:
        raise ValueError('Unrecognized assessment presentation marker')
    return text

def decorate_assessment(text):
    text=strip_assessment_presentation(text)
    blocks=assessment_blocks()
    text=text.replace('</head>',block('head',blocks['head'])+'</head>',1)
    text=text.replace('<body>','<body>'+block('header',blocks['header']),1)
    return text.replace('</body>',block('footer',blocks['footer'])+'</body>',1)
