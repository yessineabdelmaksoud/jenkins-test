from fastapi import FastAPI, Request
import uvicorn
import subprocess

app = FastAPI()

@app.post("/build-finished")
async def build_finished(request: Request):
    data = await request.json()
    job_name = data.get("name")  # nom du job
    build_number = data.get("build", {}).get("number")  # numéro du build
    status = data.get("build", {}).get("status")  # SUCCESS, FAILURE, etc.

    print(f"📢 Build terminé : {job_name} #{build_number} → {status}")

    # Vérification des données reçues
    if not job_name or not build_number:
        print("❌ Erreur: job_name ou build_number manquant dans la requête.")
        return {"status": "error", "message": "job_name ou build_number manquant"}

    # Lancer ton script d'extraction
    try:
        
        subprocess.run(["python", "extract_complete_data.py", job_name, str(build_number)])
        

    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du script: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)