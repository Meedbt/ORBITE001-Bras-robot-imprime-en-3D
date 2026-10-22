from pathlib import Path
import zipfile
root=Path(__file__).resolve().parent.parent
backup=root/'work'/'sauvegarde_v0_avant_electronique.zip'
if not backup.exists():
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.relative_to(root).parts[0] not in ['work','outputs','.git']:
                z.write(p,p.relative_to(root).as_posix())
for filename in ['build_arm.py','package_arm.py','make_viewer.py']:
    path=root/'work'/filename
    s=path.read_text(encoding='utf-8')
    s=s.replace("ROOT/'outputs'/'bras-orbite-v0'","ROOT").replace("root/'outputs'/'bras-orbite-v0'","root")
    path.write_text(s,encoding='utf-8')
path=root/'work'/'check_viewer.cjs'
s=path.read_text(encoding='utf-8').replace("/outputs/bras-orbite-v0/","/").replace("outputs/bras-orbite-v0/","")
path.write_text(s,encoding='utf-8')
print('Project generators adapted; original files preserved in work backup.')
