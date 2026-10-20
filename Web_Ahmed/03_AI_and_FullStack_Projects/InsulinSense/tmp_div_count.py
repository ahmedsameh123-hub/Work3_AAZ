from pathlib import Path
text = Path('insulin-frontend/src/components/Predict.jsx').read_text(encoding='utf-8')
print('open <div:', text.count('<div'))
print('close </div>:', text.count('</div>'))
print('difference:', text.count('<div') - text.count('</div>'))
