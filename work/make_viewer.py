import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root
template=(root/'work'/'viewer_template.html').read_text(encoding='utf-8')
lib=(root/'work'/'three.min.js').read_text(encoding='utf-8').replace('</script','<\\/script')
parts=(out/'nomenclature_pieces.json').read_text(encoding='utf-8')
data=(root/'work'/'scene.json').read_text(encoding='utf-8')
html=template.replace('/*THREE_LIBRARY*/',lib).replace('/*MODEL_DATA*/',data).replace('/*PART_DATA*/',parts)
(out/'apercu_3d.html').write_text(html,encoding='utf-8')
print('Viewer bytes:',len(html.encode()))
