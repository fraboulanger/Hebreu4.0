"""
docx2pdf.py - Convertisseur DOCX vers PDF
Version 2.1 - Correction FixedFormatExtClassPtr

Usage autonome:
    python docx2pdf.py C:\\chemin\\vers\\dossier

Usage comme module:
    from docx2pdf import convertir_docx_vers_pdf
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

log_file = None

def log_autonome(msg: str, console: bool = True) -> None:
    """Log pour mode autonome."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    if console:
        print(msg)
    if log_file:
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + "\n")
        except:
            pass

def convertir_docx_vers_pdf(
    doc_path: Path,
    pdf_path: Path,
    log_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """Convertit DOCX → PDF avec incorporation polices.
    
    Args:
        doc_path: Chemin .docx source
        pdf_path: Chemin .pdf destination  
        log_callback: Fonction log (défaut: print)
    
    Returns:
        True si succès
    """
    if log_callback is None:
        log_callback = print
    
    if not HAS_WIN32COM:
        log_callback("ERREUR : win32com non disponible")
        return False
    
    if not doc_path.exists():
        log_callback(f"ERREUR : Fichier introuvable : {doc_path}")
        return False
    
    if doc_path.suffix.lower() not in ['.doc', '.docx']:
        return False
    
    word_app = None
    doc = None
    
    try:
        import win32com.client
        word_app = win32com.client.Dispatch("Word.Application")
        word_app.Visible = False
        word_app.DisplayAlerts = 0
        
        log_callback(f"Ouverture : {doc_path.name}")
        doc = word_app.Documents.Open(str(doc_path.resolve()))
        
        log_callback(f"Export PDF : {pdf_path.name}")
        doc.ExportAsFixedFormat(
            OutputFileName=str(pdf_path.resolve()),
            ExportFormat=17,
            OpenAfterExport=False,
            OptimizeFor=0,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
            IncludeDocProps=True,
            KeepIRM=True
            # FixedFormatExtClassPtr supprimé (v2.1)
        )
        
        doc.Close(SaveChanges=False)
        word_app.Quit()
        
        if pdf_path.exists():
            taille = pdf_path.stat().st_size
            log_callback(f"✓ PDF créé ({taille:,} octets)")
            return True
        else:
            log_callback("✗ PDF non créé")
            return False
            
    except Exception as e:
        log_callback(f"✗ ERREUR : {e}")
        try:
            if doc:
                doc.Close(SaveChanges=False)
        except:
            pass
        try:
            if word_app:
                word_app.Quit()
        except:
            pass
        return False

def init_log(dossier: Path) -> None:
    global log_file
    log_file = dossier / "docx2pdf.log"
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== CONVERSION DOCX → PDF ===\n")
            f.write(f"Démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    except:
        log_file = None

def lister_fichiers_docx(dossier: Path) -> list:
    fichiers = []
    for f in dossier.iterdir():
        if f.is_file() and not f.name.startswith('~$'):
            if f.suffix.lower() in ['.doc', '.docx']:
                fichiers.append(f)
    return sorted(fichiers, key=lambda x: x.name.lower())

def main_autonome():
    print("="*60)
    print("CONVERTISSEUR DOCX → PDF v2.1")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python docx2pdf.py C:\\dossier")
        return
    
    dossier = Path(sys.argv[1])
    if not dossier.exists() or not dossier.is_dir():
        print(f"\n✗ Dossier invalide : {dossier}")
        return
    
    init_log(dossier)
    print(f"\n✓ Log : {log_file}\n")
    
    if not HAS_WIN32COM:
        print("✗ win32com non disponible")
        return
    
    fichiers = lister_fichiers_docx(dossier)
    if not fichiers:
        print("✗ Aucun fichier trouvé")
        return
    
    print(f"✓ {len(fichiers)} fichier(s)\n")
    
    succes = echecs = 0
    for fichier in fichiers:
        pdf = fichier.parent / (fichier.stem + ".pdf")
        print(f"\n→ {fichier.name}")
        if convertir_docx_vers_pdf(fichier, pdf, log_autonome):
            succes += 1
        else:
            echecs += 1
    
    print(f"\n{'='*60}")
    print(f"Total: {len(fichiers)} | ✓ {succes} | ✗ {echecs}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main_autonome()
