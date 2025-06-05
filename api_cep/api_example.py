import flet as ft
import requests
from flet import AppBar, Text, View
from flet.core.colors import Colors
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment


def main(page: ft.Page):
    # Configurações
    page.title = "Exemplo de API"
    page.theme_mode = ft.ThemeMode.DARK  # ou ft.ThemeMode.DARK
    page.window.width = 375
    page.window.height = 667

    # Funções

    # Função que retorna somente o JSON da rota
    def get_info(cep):
        url = f"https://viacep.com.br/ws/{cep}/json/"

        resposta = requests.get(url)

        if resposta.status_code == 200:
            print("Info CEP:", resposta.json())
            return resposta.json()
        else:
            return {"erro": resposta.json()}

    # função para consumir o JSON e mostrar no app
    def mostrar():
        progress.visible = True
        page.update()
        if input_cep.value == "":
            msg_error.content = ft.Text("CEP Invalido")
            page.overlay.append(msg_error)
            msg_error.open = True
        else:

            # chamar a função para pegar o JSON
            dados = get_info(int(input_cep.value))

            progress.visible = False
            page.update()

            # Verificar se a API retornou erro
            if "erro" in dados:
                page.overlay.append(msg_error)
                msg_error.open = True
            else:
                txt_rua.value = dados["logradouro"]
                txt_bairro.value = dados["bairro"]
                page.go("/segunda")

                input_cep.value = ""
                msg_sucesso.content = ft.Text("CEP Valido")
                page.overlay.append(msg_sucesso)
                msg_sucesso.open = True

        page.update()

    def gerencia_rotas(e):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    AppBar(title=Text("Home"), bgcolor=Colors.PRIMARY_CONTAINER),
                    input_cep,
                    # exemplo 1
                    btn_consultar,
                    ft.OutlinedButton(
                        text="Cancelar",
                        width=page.window.width,
                    ),

                    # exemplo 2 (cancelar sempre na esquerda)
                    ft.ResponsiveRow(
                        [
                            # Botão da esquerda
                            ft.OutlinedButton(
                                text="Cancelar",
                                col=6
                            ),

                            # Botão da direita
                            ft.FilledButton(
                                text="Consultar",
                                on_click=lambda _: mostrar(e),
                                col=6
                            ),
                        ]
                    ),
                    ft.Column(
                        [
                            progress
                        ],
                        width=page.window.width,
                        horizontal_alignment=CrossAxisAlignment.CENTER
                    ),
                ],
            )
        )

        if page.route == "/segunda":
            page.views.append(
                View(
                    "/segunda",
                    [
                        AppBar(title=Text("Segunda tela"), bgcolor=Colors.SECONDARY_CONTAINER),
                        lbl_rua,
                        txt_rua,
                        lbl_bairro,
                        txt_bairro,
                    ],
                )
            )

        page.update()

    def voltar(e):
        print("Views", page.views)
        removida = page.views.pop()
        print(removida)
        top_view = page.views[-1]
        print(top_view)
        page.go(top_view.route)


    # Componentes

    progress = ft.ProgressRing(visible=False)

    msg_sucesso = ft.SnackBar(
        content=ft.Text(""),
        bgcolor=Colors.GREEN
    )
    msg_error = ft.SnackBar(
        content=ft.Text(""),
        bgcolor=Colors.RED
    )

    input_cep = ft.TextField(
        label="CEP",
        hint_text="Ex: 16700000"
    )

    btn_consultar = ft.FilledButton(
        text="Consultar",
        width=page.window.width,
        on_click=lambda _: mostrar()
    )

    txt_rua = ft.Text(size=16)
    lbl_rua = ft.Text(value="Logradouro:", size=18, weight=FontWeight.BOLD)

    txt_bairro = ft.Text(size=16)
    lbl_bairro = ft.Text(value="Bairro:", size=18, weight=FontWeight.BOLD)

    # Eventos
    page.on_route_change = gerencia_rotas
    page.on_view_pop = voltar
    page.go(page.route)


# Comando que executa o aplicativo
# Deve estar sempre colado na linha
ft.app(main)
