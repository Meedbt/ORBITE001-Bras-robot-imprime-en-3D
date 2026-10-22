from pathlib import Path
import json,zipfile,shutil,hashlib
root=Path(__file__).resolve().parent.parent
export=root/'outputs'/'bras-orbite-v0'
export.mkdir(parents=True,exist_ok=True)
files=sorted(p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0] not in ['work','outputs','.git'])
for p in files:
    dest=export/p.relative_to(root)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
archive=root/'outputs'/'bras_orbite_v0_2.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for p in files:z.write(export/p.relative_to(root),'bras-orbite-v0/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if '/stl/' in n and n.endswith('.stl')])==38
    assert json.loads(z.read('bras-orbite-v0/sources/parametres.json'))['version']=='0.2'
    assert json.loads(z.read('bras-orbite-v0/verification_export.json'))['anomalies']==[]
    for p in files:
        assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((export/p.relative_to(root)).read_bytes()).digest()
print(json.dumps({'fichiers_pack':len(files),'STL':38,'archive':str(archive),'taille_Mo':round(archive.stat().st_size/1e6,2),'archive_verifiee':True}))
