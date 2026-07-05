"""Fingerprint every bundled paper with an LLM.

Default: calls the Anthropic API (needs ANTHROPIC_API_KEY).
`--emit-prompts`: writes each paper's prompt to data/prompts/<id>.txt instead,
for manual or agent-driven fingerprinting (write the model's JSON reply to
fingerprints/<id>.json — same location the API path uses).

Idempotent: papers with an existing valid fingerprints/<id>.json are skipped.
"""

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from prompts import SYSTEM_PROMPT, build_fingerprint_prompt  # noqa: E402
from schema import validate_fingerprint  # noqa: E402

MODEL = os.environ.get('FINGERPRINT_MODEL', 'claude-haiku-4-5-20251001')
API_URL = 'https://api.anthropic.com/v1/messages'


def call_anthropic(prompt):
    key = os.environ.get('ANTHROPIC_API_KEY')
    if not key:
        sys.exit('ANTHROPIC_API_KEY not set. Use --emit-prompts for the manual route.')
    body = json.dumps({
        'model': MODEL,
        'max_tokens': 1500,
        'system': SYSTEM_PROMPT,
        'messages': [{'role': 'user', 'content': prompt}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    return ''.join(block['text'] for block in data['content'] if block['type'] == 'text')


def parse_json_reply(text):
    text = text.strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.startswith('json'):
            text = text[4:]
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('no JSON object in reply')
    return json.loads(text[start:end + 1])


def main():
    emit_only = '--emit-prompts' in sys.argv
    bundles_dir = os.path.join(HERE, 'data', 'bundles')
    fp_dir = os.path.join(HERE, 'fingerprints')
    prompts_dir = os.path.join(HERE, 'data', 'prompts')
    os.makedirs(fp_dir, exist_ok=True)
    if emit_only:
        os.makedirs(prompts_dir, exist_ok=True)

    bundle_files = sorted(os.listdir(bundles_dir))
    done, emitted, failed = 0, 0, []
    for fn in bundle_files:
        if not fn.endswith('.json'):
            continue
        stem = fn[:-5]
        fp_path = os.path.join(fp_dir, fn)
        if os.path.exists(fp_path):
            with open(fp_path) as f:
                existing = json.load(f)
            if not validate_fingerprint(existing):
                continue  # valid fingerprint already present
        with open(os.path.join(bundles_dir, fn)) as f:
            bundle = json.load(f)
        prompt = build_fingerprint_prompt(bundle)

        if emit_only:
            with open(os.path.join(prompts_dir, stem + '.txt'), 'w') as f:
                f.write('SYSTEM:\n%s\n\nUSER:\n%s\n' % (SYSTEM_PROMPT, prompt))
            emitted += 1
            continue

        try:
            reply = call_anthropic(prompt)
            fp = parse_json_reply(reply)
            errors = validate_fingerprint(fp)
            if errors:
                raise ValueError('invalid fingerprint: %s' % errors)
            fp['_model'] = MODEL
            with open(fp_path, 'w') as f:
                json.dump(fp, f, indent=1)
            done += 1
            print('ok %s (%s, conf=%.2f)' % (
                bundle['arxiv_id'],
                fp['core_model']['object_type'],
                fp.get('confidence', -1)))
        except Exception as e:  # noqa: BLE001 — report and continue
            failed.append((bundle['arxiv_id'], str(e)))
            print('FAIL %s: %s' % (bundle['arxiv_id'], e))

    if emit_only:
        print('emitted %d prompts to %s' % (emitted, prompts_dir))
    else:
        print('fingerprinted %d, failed %d' % (done, len(failed)))


if __name__ == '__main__':
    main()
