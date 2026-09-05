from types import SimpleNamespace as NS

import run  # noqa: F401
from app import start_v440 as base
from app import patch_v7291_ztm_finish as finish
from app import patch_v729_ztm_theme as ztm
from app import presenter_v67_prod as presenter

health = dict(base._health_v440())
assert health.get('ztm_finish_version') == 'v7.2.9-final', health
assert 'ZTM' in health.get('presenter_theme',''), health
assert 'domain-adaptive' in health.get('rule11_local_case',''), health

assert finish._compact_timebox('1 min micro-case + 5 min transfer') == '1 + 5 min'
assert finish._taskbar_parts('TIMEBOX: 2 min - Use one source detail.', '2 min') == ('2 min','Use one source detail.')

bp = NS(
    lecture_title='Chapter 10 — Dependable Systems',
    engineering_thesis='Dependability, reliability, redundancy and evidence',
    source_topic_families=['Redundancy and diversity'],
)
local = finish._local_case(bp).lower()
assert 'saudi hospital' in local, local
assert 'not p1' in local, local
assert 'common-mode' in local, local

u = NS(pedagogy_content=['TRANSFER RULE — reuse the chain.', 'LOCAL CASE — hypothetical Saudi context.'])
assert 'saudi hospital' in finish._rule11_local_from_unit(bp,u).lower()

# Monkey patches must be active in the exact production import chain.
assert ztm._ppt_taskbar is finish._ppt_taskbar
assert ztm._pdf_taskbar is finish._pdf_taskbar
assert presenter.render_presenter_preview is finish._preview

print('PASS: ZTM final polish — Rule11 concrete Saudi transfer + unclipped/unduplicated timebox labels')
