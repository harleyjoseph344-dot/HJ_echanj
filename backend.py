import random
import requests
from config import MODE_TEST_SANS_TWILIO, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER

if not MODE_TEST_SANS_TWILIO:
    from twilio.rest import Client


class HJEchanjBackend:
    def __init__(self):
        self.utilisateur = {
            "non": "Jean Baptiste",
            "date_naissance": "01/01/1990",
            "mot_de_passe": "HJ1234",
            "empreinte_active": True
        }
        self.sims = {
            "+50937123456": {"nom_compte": "Jean Baptiste", "operateur": "MonCash", "balans": 5000.0},
            "+50948123456": {"nom_compte": "Jean Baptiste", "operateur": "NatCash", "balans": 5000.0}
        }
        self.benefis_app = 0.0
        self.generated_otp = None

    def verifier_internet(self):
        try:
            requests.get("https://google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    def envoyer_otp(self, numero_sim):
        if numero_sim not in self.sims:
            return False, "AUTH_FAILED"

        self.generated_otp = str(random.randint(100000, 999999))

        if MODE_TEST_SANS_TWILIO:
            return True, f"[Mode Test] Kòd 6 chif ou se : {self.generated_otp}"

        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"[HJ echanj] Code de sécurité : {self.generated_otp}",
                from_=TWILIO_NUMBER,
                to=numero_sim
            )
            return True, f"Code envoyé au {numero_sim}"
        except Exception as e:
            return False, str(e)

    def verifier_connexion(self, nom, sim, mot_de_passe, otp):
        if sim not in self.sims or self.sims[sim]["nom_compte"].lower() != nom.strip().lower():
            return False, "AUTH_FAILED"
        if mot_de_passe != self.utilisateur["mot_de_passe"]:
            return False, "PASS_ERR"
        if not self.generated_otp or otp.strip() != self.generated_otp:
            return False, "OTP_ERR"

        self.generated_otp = None
        return True, "OK"

    def executer_transaction(self, montant):
        tranches = montant / 500.0
        frais_utilisateur = tranches * 100.0
        part_app = tranches * 50.0
        part_chaque_sim = (tranches * 50.0) / 2.0

        sim_keys = list(self.sims.keys())
        self.sims[sim_keys]["balans"] += part_chaque_sim
        self.sims[sim_keys]["balans"] += part_chaque_sim
        self.benefis_app += part_app

        return {
            "frais_utilisateur": frais_utilisateur,
            "part_app": part_app,
            "part_chaque_sim": part_chaque_sim
        }

    def changer_mot_de_passe(self, otp_saisi, nouveau_mdp):
        if self.generated_otp and otp_saisi.strip() == self.generated_otp and len(nouveau_mdp) >= 4:
            self.utilisateur["mot_de_passe"] = nouveau_mdp
            self.generated_otp = None
            return True
        return False
