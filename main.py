import flet as ft
from config import LANG_DICT
from backend import HJEchanjBackend


def main(page: ft.Page):
    page.title = "HJ echanj"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 400
    page.window.height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    backend = HJEchanjBackend()
    state = {"lang": "Créole", "logged_in": False}

    def show_msg(text, color="red"):
        page.show_dialog(ft.SnackBar(ft.Text(text, color="white"), bgcolor=color))

    def render():
        page.controls.clear()
        L = LANG_DICT[state["lang"]]

        # Menu de langue (compatible Flet 1.0+)
        lang_dd = ft.Dropdown(
            value=state["lang"],
            options=[ft.dropdown.Option(x) for x in ["Créole", "Français", "Anglais", "Espagnole"]],
            width=140,
            on_select=lambda e: (state.update({"lang": e.control.value}), render()),
        )
        header = ft.Row(
            [ft.Text(L["tit"], size=24, weight=ft.FontWeight.BOLD, color="#42A5F5"), lang_dd],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.add(header, ft.Divider())

        if not state["logged_in"]:
            ent_non = ft.TextField(label=L["non"], value="Jean Baptiste")
            ent_sim = ft.TextField(label=L["sim"], value="+50937123456")
            ent_pass = ft.TextField(label=L["pass"], password=True, can_reveal_password=True)
            ent_otp = ft.TextField(label=L["otp_lbl"], width=160)

            def send_otp(e):
                if not backend.verifier_internet():
                    return show_msg(L["internet_err"])
                ok, msg = backend.envoyer_otp(ent_sim.value.strip())
                show_msg(msg, "green" if ok else "red")

            def login(e):
                if not backend.verifier_internet():
                    return show_msg(L["internet_err"])
                ok, code = backend.verifier_connexion(ent_non.value, ent_sim.value, ent_pass.value, ent_otp.value)
                if ok:
                    state["logged_in"] = True
                    render()
                else:
                    show_msg(L.get(code.lower(), L["auth_failed"]))

            def fingerprint(e):
                if not backend.verifier_internet():
                    return show_msg(L["internet_err"])
                state["logged_in"] = True
                render()

            page.add(
                ft.Text(L["login"], size=18, weight=ft.FontWeight.BOLD),
                ent_non,
                ent_sim,
                ent_pass,
                ft.Row([ent_otp, ft.Button(L["btn_otp"], on_click=send_otp)]),
                ft.Button(L["connect"], on_click=login, width=360, height=45),
                ft.OutlinedButton(f"🔒 {L['fingerprint']}", on_click=fingerprint, width=360, height=45),
            )
        else:
            sim_keys = list(backend.sims.keys())
            lbl_sim1 = ft.Text(f"SIM 1 (MonCash): {backend.sims[sim_keys[0]]['balans']:.2f} HTG", size=16)
            lbl_sim2 = ft.Text(f"SIM 2 (NatCash): {backend.sims[sim_keys[1]]['balans']:.2f} HTG", size=16)
            lbl_app = ft.Text(f"Bénéfice HJ echanj: {backend.benefis_app:.2f} HTG", size=18, weight=ft.FontWeight.BOLD, color="green")
            ent_amount = ft.TextField(label=L["amount_lbl"], keyboard_type=ft.KeyboardType.NUMBER)

            def do_trans(e):
                if not backend.verifier_internet():
                    return show_msg(L["internet_err"])
                try:
                    m = float(ent_amount.value)
                except ValueError:
                    return show_msg("Montan invalid")
                if m < 500:
                    return show_msg(L["min_err"])
                res = backend.executer_transaction(m)
                lbl_sim1.value = f"SIM 1 (MonCash): {backend.sims[sim_keys[0]]['balans']:.2f} HTG"
                lbl_sim2.value = f"SIM 2 (NatCash): {backend.sims[sim_keys[1]]['balans']:.2f} HTG"
                lbl_app.value = f"Bénéfice HJ echanj: {backend.benefis_app:.2f} HTG"
                ent_amount.value = ""
                show_msg(f"{L['success']} (+{res['part_chaque_sim']:.2f} HTG / SIM)", "green")
                page.update()

            page.add(
                ft.Card(ft.Container(ft.Column([lbl_sim1, lbl_sim2, lbl_app]), padding=15)),
                ft.Text(L["trans_tit"], size=16, weight=ft.FontWeight.BOLD),
                ent_amount,
                ft.Button(L["btn_trans"], on_click=do_trans, width=360, height=45, bgcolor="green", color="white"),
                ft.TextButton(L["logout"], on_click=lambda e: (state.update({"logged_in": False}), render())),
            )
        page.update()

    render()


ft.run(main)
