import subprocess, json, os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    os.path.join(_HERE, "sgn_parser"),
    os.path.join(_HERE, "..", "src", "sgn_parser"),
    os.path.join(_HERE, "..", "files", "src", "sgn_parser"),
]

def _find_binary():
    return next((p for p in _CANDIDATES if os.path.isfile(p)), None)

def analyser(chemin_sgn, chemin_binaire=None):
    bin_path = chemin_binaire or _find_binary()
    if not bin_path:
        return {"erreurs": [{"ligne": 0, "message": "sgn_parser introuvable. Lancez make dans src/"}]}
    try:
        res = subprocess.run([bin_path, chemin_sgn],
                             capture_output=True, text=True, timeout=15)
        if res.stdout.strip():
            return json.loads(res.stdout)
        erreurs = [{"ligne": 0, "message": l.strip()}
                   for l in res.stderr.splitlines() if l.strip()]
        return {"niveaux": [], "erreurs": erreurs or [{"ligne": 0, "message": "Sortie vide"}]}
    except json.JSONDecodeError as e:
        return {"erreurs": [{"ligne": 0, "message": f"JSON invalide : {e}"}]}
    except Exception as e:
        return {"erreurs": [{"ligne": 0, "message": str(e)}]}
