import flet as ft
from flet.core.app_bar import AppBar
from flet.core.colors import Colors
from flet.core.elevated_button import ElevatedButton
from flet.core.text_style import TextStyle
from flet.core.textfield import TextField
from flet.core.border import Border


def main(page: ft.Page):
    page.title = "Livraria"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 375
    page.window.height = 667
    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
        "istokWeb-Bold": "/fonts/IstokWeb-Bold.ttf",
        "istokWeb-Bolditalic": "/fonts/IstokWeb-BoldItalic.ttf",
        "IstokWeb-Italic": "/fonts/IstokWeb-Italic.ttf",
        "IstokWeb-Regular": "/fonts/IstokWeb-Regular.ttf",
    }
    page.TextStyle = ft.TextStyle(font_family="IstokWeb-Regular")

    def gerencia_rotas(e):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Container(
                        alignment=ft.alignment.center,
                        padding=10,
                        content=ft.Column(
                            [
                                ft.Container(height=40),
                                ft.Image(
                                    src=f"icons/book.png",
                                    width=168,
                                    height=168,
                                    fit=ft.ImageFit.CONTAIN,
                                ),
                                ft.Text("Discover. Borrow.\nRead.", size=38, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=140),
                                ft.CupertinoButton(
                                    text="Get Started",
                                    bgcolor=ft.Colors.BLACK,
                                    color=ft.Colors.WHITE,
                                    width=320,
                                    on_click=lambda _: page.go("/sign_in")
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    )
                ]
            )
        )
        if page.route == "/sign_in" or page.route == "/forgot_password":
            page.views.append(
                ft.View(
                    "/sign_in",
                    [
                        ft.Container(
                            alignment=ft.alignment.center,
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Container(height=40),
                                    ft.Text("Sign In", size=38, weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=5),
                                    input_email,
                                    input_senha,
                                    ft.Container(
                                        alignment=ft.alignment.center_right,
                                        content=ft.Column([
                                            ft.TextButton(text="Forgot password?",on_click=lambda _: page.go("/forgot_password")),
                                        ]
                                        ),
                                    ),
                                    ft.CupertinoButton(
                                        text="Sign In",
                                        bgcolor=ft.Colors.BLACK,
                                        color=ft.Colors.WHITE,
                                        width=320,
                                        on_click=lambda _: page.go("/home")),
                                    ft.OutlinedButton(
                                        width=320,
                                        height=50,
                                        content=ft.Row(
                                            [
                                                ft.Icon(name=ft.Icons.ACCOUNT_BOX, color="black"),
                                                ft.Text("Sign in with Google"),
                                            ],
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        width=320,
                                        height=50,
                                        content=ft.Row(
                                            [
                                                ft.Icon(name=ft.Icons.ACCOUNT_BOX, color="blue"),
                                                ft.Text("Sign in with Facebook"),
                                            ],
                                        ),
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text("Don't have an account?"),
                                            ft.TextButton("Sign up")
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=-4
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START
                            )
                        )
                    ]
                )
            )
            if page.route == "/forgot_password":
                page.views.append(
                    ft.View(
                        "/forgot_password",
                        [
                            ft.AppBar(title=ft.Text("Forgot Password"),bgcolor=ft.Colors.BLACK,color=ft.Colors.WHITE),
                        ]
                    )
                )
        page.update()

    def voltar(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    input_email = ft.TextField(label="Email Address")
    input_senha = ft.TextField(label="Password")

    page.on_route_change = gerencia_rotas
    page.on_view_pop = voltar

    page.go(page.route)


ft.app(main)