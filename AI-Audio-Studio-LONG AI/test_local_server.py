import json
import urllib.request

def test_api():
    base = 'http://127.0.0.1:8001'
    
    # 1. Info
    r = json.loads(urllib.request.urlopen(f'{base}/api/info').read().decode())
    assert r['branding']['developer']['name'] == 'LONG AI', 'Branding dev name mismatch'
    print('1. /api/info: OK (Developer: LONG AI)')
    
    # 2. Health
    h = json.loads(urllib.request.urlopen(f'{base}/api/health').read().decode())
    assert h['ok'] is True, 'Health check failed'
    loaded = h['status']['loaded']
    sr = h['status']['sample_rate']
    print(f'2. /api/health: OK (Loaded: {loaded}, Sample Rate: {sr} Hz)')
    
    # 3. Warmup
    req = urllib.request.Request(f'{base}/api/warmup', data=b'', method='POST')
    w = json.loads(urllib.request.urlopen(req).read().decode())
    assert w['ok'] is True, 'Warmup failed'
    print('3. /api/warmup: OK')
    
    # 4. Voices
    v = json.loads(urllib.request.urlopen(f'{base}/api/voices').read().decode())
    voice_list = v.get('voices', [])
    assert len(voice_list) >= 20, f'Too few voices: {len(voice_list)}'
    print(f'4. /api/voices: OK ({len(voice_list)} preset voices found)')
    
    # 5. TTS Synthesize
    data = json.dumps({'text': 'Xin chào, đây là bài kiểm tra độ ổn định của hệ thống.', 'voice': 'Trúc Ly'}).encode('utf-8')
    req = urllib.request.Request(f'{base}/api/tts', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    audio = urllib.request.urlopen(req).read()
    assert len(audio) > 10000, f'Audio too short: {len(audio)} bytes'
    print(f'5. /api/tts: OK (Generated {len(audio)} bytes WAV audio)')
    
    # 6. Conversation
    conv_data = json.dumps({
        'turns': [
            {'voice': 'Trúc Ly', 'text': 'Chào bạn! Mình là Trúc Ly.'},
            {'voice': 'Adam bựa', 'text': 'Chào Trúc Ly, mình là Adam.'}
        ]
    }).encode('utf-8')
    req = urllib.request.Request(f'{base}/api/conversation', data=conv_data, headers={'Content-Type': 'application/json'}, method='POST')
    conv_audio = urllib.request.urlopen(req).read()
    assert len(conv_audio) > 20000, f'Conversation audio too short: {len(conv_audio)} bytes'
    print(f'6. /api/conversation: OK (Generated {len(conv_audio)} bytes multi-speaker dialogue)')
    
    print('\n======================================================')
    print('SUCCESS: TAT CA 6 BAI TEST API CHAY LOCAL DA VUOT QUA 100% ON DINH!')
    print('======================================================')

if __name__ == '__main__':
    test_api()
